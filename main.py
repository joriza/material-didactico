#!/usr/bin/env python3
"""z-material-didactico — generador spec-driven (Python + Jinja2).

Tareas: a1, a2, b1-b5. Naming: <sigla>-<nro_eje><nro_clase_eje>-<Tarea>-<nombre_≤50>.md
"""
import argparse
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
BASE_COMUN = ROOT / "base-comun"
MATERIAS = ROOT / "materias"
OUTPUT = ROOT / "output"

TAREA_LEGIBLE = {
    "a1": "Plan_Anual", "a2": "Plan_De_Clases",
    "b1": "Material_Didactico", "b2": "Actividad_Aulica",
    "b4": "Respuestas_Actividad", "b5": "Planificacion_Aulica",
    "b6": "Guia_Docente",
    "c1": "Cuestionario_Evaluacion", "c2": "Respuestas_Evaluacion",
    "d1": "Actividad_Integradora", "d2": "Respuestas_Integradora",
}

TAREA_TEMPLATE = {
    "a1": "tareas/tarea-plan_anual.md",
    "a2": "tareas/tarea-plan_de_clases.md",
    "b1": "tareas/tarea-material_didactico.md",
    "b2": "tareas/tarea-actividad_aulica.md",
    "b4": "tareas/tarea-respuestas_actividad_aulica.md",
    "b5": "tareas/tarea-planificacion_aulica.md",
    "b6": "tareas/tarea-guia_docente.md",
}

TAREAS_B = ["b1", "b2", "b4", "b5", "b6"]


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def parse_config_datos(path: Path) -> dict:
    variables = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*-\s*\*\*([^*]+)\*\*\s*:\s*(.+?)\s*$", line)
        if m:
            variables[m.group(1).strip()] = m.group(2).strip()
    return variables


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _find_latest(directory: Path, pattern: str):
    matches = sorted(Path(directory).glob(pattern))
    return matches[-1] if matches else None


def _fmt_duracion(s: float) -> str:
    """Segundos -> '12.3s' (< 1 min) o 'Xm YYs' (>= 1 min)."""
    if s < 59.95:  # umbral: a partir de 59.95, .1f redondearia a "60.0s"
        return f"{s:.1f}s"
    total = round(s)
    m, rest = divmod(total, 60)
    return f"{m}m {rest:02d}s"


# --------------------------------------------------------------------------
# a2 — tabla de clases (9 columnas canónicas)
# --------------------------------------------------------------------------
def _canon_key(k: str) -> str:
    """Normaliza el encabezado de columna a una clave canónica."""
    k = _strip_accents(k.strip().lower())
    explicit = {
        "nro_eje": "nro_eje", "nro eje": "nro_eje", "numero de eje": "nro_eje",
        "nº eje": "nro_eje", "nro. eje": "nro_eje", "n_eje": "nro_eje",
        "nro_clase_eje": "nro_clase_eje", "nro clase eje": "nro_clase_eje",
        "nº clase eje": "nro_clase_eje", "clase_eje": "nro_clase_eje", "clase eje": "nro_clase_eje",
        "eje": "eje_descripcion", "eje tematico": "eje_descripcion",
        "carácter/objetivo": "caracter", "caracter/objetivo": "caracter",
        "carácter": "caracter", "caracter": "caracter", "objetivo": "caracter",
        "tema del día": "tema", "tema del dia": "tema", "tema": "tema",
        "actividades": "actividades", "fecha": "fecha", "id": "id",
        "tema_nro": "tema_nro", "tema nro": "tema_nro", "nro_tema": "tema_nro",
        "nro tema": "tema_nro", "numero de tema": "tema_nro", "tema numero": "tema_nro",
        "nº tema": "tema_nro", "nº de tema": "tema_nro", "tema nº": "tema_nro",
        "nº clase": "nro_clase_viejo", "nro clase": "nro_clase_viejo",
    }
    if k in explicit:
        return explicit[k]
    return re.sub(r"^n[oºro.\s]+", "", k).strip() or k


def parse_a2_table(path: Path) -> list[dict]:
    """Parsea la tabla Markdown de a2 → lista de dicts con claves canónicas."""
    rows, header = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.split("|")[1:-1]]
        if not cells:
            continue
        if header is None:
            header = [_canon_key(c) for c in cells]
            continue
        if all(re.fullmatch(r"[:\s-]*", c) for c in cells):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def filter_by_eje(rows: list[dict], nro_eje, nro_clase_eje=None) -> list[dict]:
    out = []
    for r in rows:
        if str(r.get("nro_eje", "")).strip() != str(nro_eje).strip():
            continue
        if nro_clase_eje is not None and str(r.get("nro_clase_eje", "")).strip() != str(nro_clase_eje).strip():
            continue
        out.append(r)
    return out


# --------------------------------------------------------------------------
# Jinja2
# --------------------------------------------------------------------------
def make_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(BASE_COMUN)), trim_blocks=True, lstrip_blocks=True)


def render(env: Environment, template_rel: str, variables: dict) -> str:
    return env.get_template(template_rel).render(**variables)


# --------------------------------------------------------------------------
# LLM
# --------------------------------------------------------------------------
def load_client(config_llm_path: Path, provider=None, model_override=None):
    cfg = json.loads(config_llm_path.read_text(encoding="utf-8"))
    providers = cfg.get("provider", {})
    key = provider or cfg.get("default") or next(iter(providers))
    p = providers[key]
    opts = p.get("options", {})
    base_url = opts["baseURL"]
    api_key = (opts.get("apiKey") or opts.get("api_key") or "").strip()
    if not api_key:
        if "localhost" in base_url or "127.0.0.1" in base_url:
            api_key = "dummy-key"
        else:
            api_key = os.environ.get("ZHIPU_API_KEY", "")
    if not api_key:
        raise SystemExit(f"Falta API key para provider '{key}'.")
    model = model_override or next(iter(p.get("models", {})))
    disable_thinking = bool(p.get("disableThinking", False))
    return OpenAI(base_url=base_url, api_key=api_key), model, key, base_url, disable_thinking


def call_llm(client, model, prompt, disable_thinking=False, temperature=0.2, max_tokens=16384) -> str:
    extra_body = {"chat_template_kwargs": {"enable_thinking": False}} if disable_thinking else None
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        extra_body=extra_body,
    )
    texto = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        content = getattr(delta, "content", None) if delta else None
        if content:
            texto += content
            print(content, end="", flush=True)
    print()
    return texto


# --------------------------------------------------------------------------
# Naming
# --------------------------------------------------------------------------
def nombre_ref(titulo: str, max_len: int = 50) -> str:
    """Titulo → Nombre_Referencial: primera mayúscula + _, sin tildes, ≤ max_len."""
    s = _strip_accents(titulo).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "material"
    s = s[0].upper() + s[1:]
    if len(s) > max_len:
        s = s[:max_len]
    return s


def pascal(texto: str) -> str:
    palabras = re.split(r"[\s\-_]+", _strip_accents(texto))
    return "_".join(p.capitalize() for p in palabras if p)


def nombre_archivo(sigla, nro_eje, nro_clase_eje, tarea_code, nombre_referencial, tema_nro=None, multi=False) -> str:
    """Arma el nombre de archivo. Si multi=True, appendea el dígito del tema al código de clase."""
    codigo = f"{sigla}-{nro_eje}{nro_clase_eje}"
    if multi and tema_nro is not None:
        if not str(tema_nro).isdigit() or int(tema_nro) > 9:
            raise SystemExit(f"Tema_Nro debe ser un dígito (1-9). Recibido: {tema_nro!r}")
        codigo += str(tema_nro)
    tarea_leg = TAREA_LEGIBLE.get(tarea_code, pascal(tarea_code))
    return f"{codigo}-{tarea_leg}-{nombre_referencial}.md"


def _prefijo_codigo(sigla, nro_eje, nro_clase_eje, tema_nro=None, multi=False) -> str:
    """Devuelve el prefijo de código de clase (sin guion final ni tarea)."""
    codigo = f"{sigla}-{nro_eje}{nro_clase_eje}"
    if multi and tema_nro is not None:
        codigo += str(tema_nro)
    return codigo


def extraer_titulo(doc: str) -> str:
    for line in doc.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("# ").strip()
    for line in doc.splitlines():
        if line.strip():
            return line.strip()
    return "documento"


def _nombre_ref_de_b1(sigla, nro_eje, nro_clase_eje, tema_nro=None, multi=False):
    """Busca el archivo b1 de esa clase+tema y extrae su Nombre_Referencial (compartido)."""
    pref = _prefijo_codigo(sigla, nro_eje, nro_clase_eje, tema_nro, multi) + "-Material_Didactico-"
    f = _find_latest(OUTPUT, f"{pref}*.md")
    if not f:
        return None
    return f.stem[len(pref):]


def _existe_output(sigla, nro_eje, nro_clase_eje, tarea_code, tema_nro=None, multi=False):
    """Verifica si ya existe el output de una tarea para una clase+tema."""
    tarea_leg = TAREA_LEGIBLE[tarea_code]
    pref = _prefijo_codigo(sigla, nro_eje, nro_clase_eje, tema_nro, multi) + f"-{tarea_leg}-"
    # Match exacto del dígito de tema: exigir guion tras el código para no colisionar
    # IRI-11-... (mono) vs IRI-111-... (multi): el guion actúa como delimitador.
    return bool(_find_latest(OUTPUT, f"{pref}*.md"))


# --------------------------------------------------------------------------
# Validación de longitud del output (marcador @validar en plantillas)
# --------------------------------------------------------------------------
_VALIDAR_RE = re.compile(r"\{#\s*@validar:\s*(\w+)\s+(min|max)\s*=\s*(\d+)\s*#\}")


def _leer_reglas_validacion(tarea_code):
    """Lee el marcador @validar de la plantilla CRUDA (no renderizada).
    Devuelve lista de tuplas (medida, operador, valor). [] si no hay marcador.
    El marcador es un comentario Jinja {# @validar: <medida> <min|max>=<n> #}
    que Jinja NO incluye en el render, así que no contamina el prompt."""
    tmpl_path = BASE_COMUN / TAREA_TEMPLATE[tarea_code]
    texto = tmpl_path.read_text(encoding="utf-8")
    return [(m.group(1), m.group(2), int(m.group(3))) for m in _VALIDAR_RE.finditer(texto)]


def _extraer_parrafo_sintesis(doc):
    """Extrae el primer párrafo sustantivo del documento (la síntesis ultracomprimida de b6).
    Heurística: partir por líneas en blanco en bloques; descartar títulos (#, ##),
    líneas de encabezado (Materia:, Docente:, Eje temático:, Tema:) y bloques vacíos.
    Devolver el primer bloque con contenido real."""
    _HEAD_ENCABEZADO = ("materia:", "docente:", "eje temático:", "tema:")
    bloques = [b.strip() for b in re.split(r"\n\s*\n", doc)]
    for b in bloques:
        if not b:
            continue
        primera_linea = b.splitlines()[0].strip().lower()
        # saltar títulos markdown y encabezados
        if primera_linea.startswith("#"):
            continue
        if any(primera_linea.startswith(h) for h in _HEAD_ENCABEZADO):
            continue
        return b
    return doc  # fallback: todo el doc


def _validar_caracter(doc, tarea_code):
    """Cuenta caracteres del output y AVISA (no bloquea) si no cumple las reglas
    @validar declaradas en la plantilla. El umbral vive en la plantilla (single source
    of truth): cambiar el número ahí actualiza la validación sin tocar código."""
    reglas = _leer_reglas_validacion(tarea_code)
    if not reglas:
        return
    for medida, op, valor in reglas:
        if medida == "doc_entero":
            n = len(doc)
        elif medida == "parrafo_sintesis":
            n = len(_extraer_parrafo_sintesis(doc))
        else:
            continue
        if op == "min" and n < valor:
            print(f"  ⚠ {tarea_code} ({medida}): {n} caracteres — faltan {valor - n} para el mínimo de {valor}.")
        elif op == "max" and n > valor:
            print(f"  ⚠ {tarea_code} ({medida}): {n} caracteres — excede el máximo de {valor} por {n - valor}.")


def resolver_cascada_b(tarea_code, manifest):
    """Resuelve el subárbol de una tarea tipo b: prerrequisitos + tarea + dependientes.
    Devuelve lista en orden topológico (sólo tipo b; a1/a2 se verifican aparte)."""
    visitados = set()
    orden = []

    def visitar(t):
        if t in visitados or t not in TAREAS_B:
            return
        visitados.add(t)
        for prereq in manifest.get("tareas", {}).get(t, {}).get("depende_de", []):
            visitar(prereq)
        orden.append(t)
        for dep in manifest.get("tareas", {}).get(t, {}).get("dependientes", []):
            visitar(dep)

    visitar(tarea_code)
    return orden


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
SOBRESCRIBIR_SIN_PREGUNTAR = False


def write_output(path: Path, content: str):
    global SOBRESCRIBIR_SIN_PREGUNTAR
    if path.exists() and not SOBRESCRIBIR_SIN_PREGUNTAR:
        r = input(f"\nEl archivo '{path.name}' ya existe. ¿Sobrescribir? [S/n]: ").strip().lower()
        if r and r != "s":
            print("→ Se omite (no se sobrescribe).")
            return None
    path.write_text(content, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Orquestación
# --------------------------------------------------------------------------
def _cargar_comun(args):
    materia_dir = MATERIAS / args.materia
    if not materia_dir.exists():
        raise SystemExit(f"No existe la materia '{args.materia}' en {MATERIAS}")
    vars_cfg = parse_config_datos(materia_dir / "config-datos.md")
    contenidos_path = materia_dir / "datos-contenidos_minimos.md"
    contenidos = contenidos_path.read_text(encoding="utf-8") if contenidos_path.exists() else ""
    env = make_env()
    client, model, _, _, dt = load_client(BASE_COMUN / "config-llm.json", args.provider, args.modelo)
    print(f"→ LLM: provider={args.provider or '(default)'} model={model}")
    return materia_dir, vars_cfg, contenidos, env, (client, model, dt)


def run_a1(args):
    _, vars_cfg, contenidos, env, (client, model, dt) = _cargar_comun(args)
    variables = {**vars_cfg, "contenidos_minimos": contenidos,
                 "Reglas_ciclo_lectivo": vars_cfg.get("Reglas_ciclo_lectivo", ""),
                 "Reglas_cuatrimestres": vars_cfg.get("Reglas_cuatrimestres", "")}
    prompt = render(env, TAREA_TEMPLATE["a1"], variables)
    if args.dry_run:
        print("\n--- PROMPT (dry-run, a1) ---\n" + prompt)
        return []
    print(f"\n=== a1 — Plan Anual de {args.materia} ===")
    t0 = time.time()
    doc = call_llm(client, model, prompt, dt)
    titulo = extraer_titulo(doc)
    ref = "Plan_anual" if titulo.lower().startswith("plan") else nombre_ref(titulo)
    fname = f"{args.materia}-Plan_Anual-{ref}.md"
    print(f"\n⏱  {time.time() - t0:.1f}s")
    r = write_output(OUTPUT / fname, doc)
    return [(fname, doc)] if r else []


def run_a2(args):
    _, vars_cfg, contenidos, env, (client, model, dt) = _cargar_comun(args)
    a1_path = Path(args.a1) if args.a1 else _find_latest(OUTPUT, f"{args.materia}-Plan_Anual-*.md")
    if not a1_path or not a1_path.exists():
        raise SystemExit("No se encontró a1. Generá a1 primero o usá --a1 <ruta>.")
    variables = {**vars_cfg, "contenidos_minimos": contenidos,
                 "planificacion_anual": a1_path.read_text(encoding="utf-8")}
    print(f"→ Usando a1: {a1_path.name}")
    prompt = render(env, TAREA_TEMPLATE["a2"], variables)
    if args.dry_run:
        print("\n--- PROMPT (dry-run, a2) ---\n" + prompt)
        return []
    print(f"\n=== a2 — Plan de Clases de {args.materia} ===")
    t0 = time.time()
    doc = call_llm(client, model, prompt, dt)
    fname = f"{args.materia}-Plan_De_Clases-Libro_de_temas.md"
    print(f"\n⏱  {time.time() - t0:.1f}s")
    r = write_output(OUTPUT / fname, doc)
    return [(fname, doc)] if r else []


def _insumo(args, tarea_dep, tema_nro=None, multi=False):
    """Lee el output de una tarea dependiente (b1/b2) para la clase+tema actual."""
    tarea_leg = TAREA_LEGIBLE[tarea_dep]
    pref = _prefijo_codigo(args.materia, args.eje, args.clase_eje, tema_nro, multi) + f"-{tarea_leg}-"
    f = _find_latest(OUTPUT, f"{pref}*.md")
    if not f:
        tema_suf = f" (tema {tema_nro})" if multi else ""
        raise SystemExit(f"No se encontró output de '{tarea_dep}' para esta clase{tema_suf}. Generá {tarea_dep} primero.")
    return f.read_text(encoding="utf-8")


def run_b1(args, tema_row, tema_nro=None, multi=False):
    _, vars_cfg, contenidos, env, (client, model, dt) = _cargar_comun(args)
    variables = {**vars_cfg,
                 "eje_numero": tema_row.get("nro_eje", args.eje),
                 "eje_descripcion": tema_row.get("eje_descripcion", ""),
                 "tema": tema_row.get("tema", ""),
                 "actividades": tema_row.get("actividades", ""),
                 "contenidos_minimos": contenidos}
    prompt = render(env, TAREA_TEMPLATE["b1"], variables)
    if args.dry_run:
        print("\n--- PROMPT (dry-run, b1) ---\n" + prompt)
        return []
    tema_suf = f", tema {tema_nro}" if multi else ""
    print(f"\n=== [{args.materia}] b1 — Material Didáctico (eje {args.eje}, clase-eje {args.clase_eje}{tema_suf}) ===")
    t0 = time.time()
    doc = call_llm(client, model, prompt, dt)
    _validar_caracter(doc, "b1")
    ref = nombre_ref(extraer_titulo(doc))
    fname = nombre_archivo(args.materia, args.eje, args.clase_eje, "b1", ref, tema_nro=tema_nro, multi=multi)
    print(f"\n⏱  {time.time() - t0:.1f}s")
    r = write_output(OUTPUT / fname, doc)
    return [(fname, doc)] if r else []


def run_b2_b5(args, tarea_code, tema_row, tema_nro=None, multi=False):
    _, vars_cfg, _, env, (client, model, dt) = _cargar_comun(args)
    variables = {**vars_cfg,
                 "eje_numero": tema_row.get("nro_eje", args.eje),
                 "eje_descripcion": tema_row.get("eje_descripcion", ""),
                 "tema": tema_row.get("tema", ""),
                 "actividades": tema_row.get("actividades", "")}
    if tarea_code in ("b2", "b5", "b6"):
        variables["material_didactico"] = _insumo(args, "b1", tema_nro=tema_nro, multi=multi)
    if tarea_code == "b4":
        variables["actividad_aulica"] = _insumo(args, "b2", tema_nro=tema_nro, multi=multi)
    prompt = render(env, TAREA_TEMPLATE[tarea_code], variables)
    if args.dry_run:
        print(f"\n--- PROMPT (dry-run, {tarea_code}) ---\n" + prompt)
        return []
    tema_suf = f", tema {tema_nro}" if multi else ""
    print(f"\n=== [{args.materia}] {tarea_code} — {TAREA_LEGIBLE[tarea_code]} (eje {args.eje}, clase-eje {args.clase_eje}{tema_suf}) ===")
    t0 = time.time()
    doc = call_llm(client, model, prompt, dt)
    _validar_caracter(doc, tarea_code)
    ref = _nombre_ref_de_b1(args.materia, args.eje, args.clase_eje, tema_nro=tema_nro, multi=multi) or nombre_ref(extraer_titulo(doc))
    fname = nombre_archivo(args.materia, args.eje, args.clase_eje, tarea_code, ref, tema_nro=tema_nro, multi=multi)
    print(f"\n⏱  {time.time() - t0:.1f}s")
    r = write_output(OUTPUT / fname, doc)
    return [(fname, doc)] if r else []


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    global SOBRESCRIBIR_SIN_PREGUNTAR
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="z-material-didactico (generador spec-driven)")
    ap.add_argument("--materia", required=True, help="sigla de materia (ej: IRI)")
    ap.add_argument("--tarea", default="b1", help="a1 | a2 | b1-b5")
    ap.add_argument("--eje", help="nro_eje (ej: 1)")
    ap.add_argument("--clase-eje", dest="clase_eje", help="nro_clase_eje (ej: 1)")
    ap.add_argument("--id", help="id global de la fila (alternativa a --eje/--clase-eje)")
    ap.add_argument("--tema-idx", dest="tema_idx",
                    help="Tema_Nro puntual dentro del encuentro (multi-tema). Si se omite, procesa todos.")
    ap.add_argument("--a2", help="ruta a un a2 (plan de clases) alternativo")
    ap.add_argument("--a1", help="ruta a un a1 (plan anual) alternativo")
    ap.add_argument("--provider", help="provider de config-llm.json")
    ap.add_argument("--modelo", help="id de modelo (sobreescribe)")
    ap.add_argument("--dry-run", action="store_true", help="arma y muestra el prompt sin llamar al LLM")
    args = ap.parse_args(argv)
    args.materia = args.materia.upper()  # naming siempre en mayúsculas

    OUTPUT.mkdir(exist_ok=True)
    tarea = args.tarea
    docs = []

    if tarea == "a1":
        docs = run_a1(args)
    elif tarea == "a2":
        docs = run_a2(args)
    elif tarea in TAREAS_B:
        if args.eje is not None and str(args.eje) == "0":
            print("→ nro_eje=0 (clase sin dictado): no se generan archivos tipo b.")
            return
        if args.clase_eje is not None and args.eje is None:
            raise SystemExit("--clase-eje requiere --eje N.")

        # Verificar prerrequisitos a1 y a2 (anuales). Generar automáticamente si faltan.
        a2_path = Path(args.a2) if args.a2 else _find_latest(OUTPUT, f"{args.materia}-Plan_De_Clases-*.md")
        if not a2_path or not a2_path.exists():
            print("→ a2 no encontrado. Generando a1 y a2 automáticamente...")
            a1_path = Path(args.a1) if args.a1 else _find_latest(OUTPUT, f"{args.materia}-Plan_Anual-*.md")
            if not a1_path or not a1_path.exists():
                print("\n=== Generando a1 (Plan Anual) ===")
                run_a1(args)
            print("\n=== Generando a2 (Plan de Clases) ===")
            run_a2(args)
            a2_path = _find_latest(OUTPUT, f"{args.materia}-Plan_De_Clases-*.md")
            if not a2_path:
                raise SystemExit("No se pudo generar a2. Verificá el LLM y volvé a intentar.")

        rows = parse_a2_table(a2_path)

        # Determinar las clases a procesar (jerarquía de especificidad)
        if args.id:
            id_row = next((r for r in rows if str(r.get("id", "")).strip() == str(args.id).strip()), None)
            if not id_row:
                raise SystemExit(f"No se encontró id={args.id} en {a2_path.name}")
            clases_a_procesar = [(id_row.get("nro_eje", args.eje), id_row.get("nro_clase_eje", "0"))]
        elif args.eje is not None and args.clase_eje is not None:
            clases_a_procesar = [(args.eje, args.clase_eje)]
        elif args.eje is not None:
            # TODAS las clases del eje (nro_clase_eje != 0)
            clases_unicas = sorted(set(
                str(r.get("nro_clase_eje", "0")).strip()
                for r in rows
                if str(r.get("nro_eje", "")).strip() == str(args.eje).strip()
                and str(r.get("nro_clase_eje", "0")).strip() != "0"
            ), key=lambda x: int(x) if x.isdigit() else 0)
            clases_a_procesar = [(args.eje, ce) for ce in clases_unicas]
        else:
            # TODOS los ejes con dictado (nro_eje != 0, nro_clase_eje != 0)
            clases_a_procesar = sorted(set(
                (str(r.get("nro_eje", "")).strip(), str(r.get("nro_clase_eje", "0")).strip())
                for r in rows
                if str(r.get("nro_eje", "")).strip() not in ("0", "")
                and str(r.get("nro_clase_eje", "0")).strip() != "0"
            ), key=lambda p: (int(p[0]), int(p[1])))

        if args.eje is None:
            SOBRESCRIBIR_SIN_PREGUNTAR = True
            print(f"→ [{args.materia}] Modo multi-eje: {len(clases_a_procesar)} clase(s) en todos los ejes con dictado. Sobrescribiendo sin preguntar.")
        elif len(clases_a_procesar) > 1:
            SOBRESCRIBIR_SIN_PREGUNTAR = True
            print(f"→ [{args.materia}] Modo multi-clase: {len(clases_a_procesar)} clase(s) del eje {args.eje}. Sobrescribiendo sin preguntar.")

        manifest = load_yaml(BASE_COMUN / "tareas.yaml")

        for eje_val, clase_eje_val in clases_a_procesar:
            args.eje = eje_val
            args.clase_eje = clase_eje_val
            clase_rows = filter_by_eje(rows, eje_val, clase_eje_val)
            if not clase_rows:
                print(f"  ⚠ No se encontró eje={eje_val} clase-eje={clase_eje_val}, saltando.")
                continue
            multi = len(clase_rows) > 1
            # Ordenar por Tema_Nro (default 1 si falta)
            clase_rows = sorted(
                clase_rows,
                key=lambda r: int(r.get("tema_nro", "1")) if str(r.get("tema_nro", "1")).isdigit() else 1
            )
            encuentros_desc = "multi-tema" if multi else "mono-tema"
            print(f"\n========== [{args.materia}] Clase eje={eje_val} clase-eje={clase_eje_val} ({encuentros_desc}, "
                  f"{len(clase_rows)} tema(s)) ==========")
            for tema_row in clase_rows:
                tema_nro = tema_row.get("tema_nro", "1")
                if args.tema_idx is not None and str(args.tema_idx).strip() != str(tema_nro).strip():
                    continue
                print(f"\n----- Tema {tema_nro}: {tema_row.get('tema', '')} -----")
                cascada = resolver_cascada_b(tarea, manifest)
                print(f"  Cascada: {' → '.join(cascada)}")
                b1_existe = _existe_output(args.materia, eje_val, clase_eje_val, "b1", tema_nro=tema_nro, multi=multi)
                for t in cascada:
                    suf = f" (tema {tema_nro})" if multi else ""
                    if t == "b1":
                        if b1_existe:
                            print(f"  → b1 ya existe{suf}, saltando.")
                            continue
                    else:
                        existe_t = _existe_output(args.materia, eje_val, clase_eje_val, t, tema_nro=tema_nro, multi=multi)
                        if b1_existe:
                            if existe_t:
                                print(f"  → {t} ya existe{suf}, saltando.")
                                continue
                        elif existe_t:
                            print(f"  → {t} colgado (sin b1), regenerando.")
                    if t == "b1":
                        docs += run_b1(args, tema_row, tema_nro=tema_nro, multi=multi)
                    else:
                        docs += run_b2_b5(args, t, tema_row, tema_nro=tema_nro, multi=multi)

        print(f"\n>>> {len(clases_a_procesar)} clase(s) procesada(s), {len(docs)} documento(s) generado(s). <<<")
    else:
        raise SystemExit(f"Tarea '{tarea}' no implementada todavía.")

    print("\n=== Generados ===")
    for fname, _ in docs:
        print(" -", fname)


if __name__ == "__main__":
    _t0_total = time.time()
    try:
        main()
    finally:
        print(f"\n⏱  Total: {_fmt_duracion(time.time() - _t0_total)}")
