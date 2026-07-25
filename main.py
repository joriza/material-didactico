#!/usr/bin/env python3
"""z-material-didactico — generador spec-driven de material didáctico (Python + Jinja2).

v1: flujo de la tarea b1 (material didáctico) sobre una clase de a2.
    Lee config-llm.json, config-datos.md y a2 (plan de clases); renderiza la
    plantilla Jinja2 (tarea que hereda la base común); llama al LLM con
    streaming; arma el naming; escribe en output/ (con confirmación de
    sobrescritura). Las demás tareas y el DAG completo se añaden después.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
BASE_COMUN = ROOT / "base-comun"
MATERIAS = ROOT / "materias"
OUTPUT = ROOT / "output"

# Nombre legible de cada tarea para el naming (PascalCase con _).
TAREA_LEGIBLE = {
    "a1": "Plan_Anual",
    "a2": "Plan_De_Clases",
    "b1": "Material_Didactico",
    "b2": "Actividad_Aulica",
    "b3": "Sintesis",
    "b4": "Respuestas_Actividad",
    "b5": "Planificacion_Aulica",
    "c1": "Cuestionario_Evaluacion",
    "c2": "Respuestas_Evaluacion",
    "d1": "Actividad_Integradora",
    "d2": "Respuestas_Integradora",
}

# Archivo de plantilla por código de tarea (debe coincidir con tareas.yaml).
TAREA_TEMPLATE = {
    "a1": "tareas/tarea-plan_anual.md",
    "a2": "tareas/tarea-plan_de_clases.md",
    "b1": "tareas/tarea-material_didactico.md",
    "b2": "tareas/tarea-actividad_aulica.md",
}


# --------------------------------------------------------------------------
# Carga de datos
# --------------------------------------------------------------------------
def parse_config_datos(path: Path) -> dict:
    """Parse '- **Clave**: valor' de config-datos.md -> dict."""
    variables = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*-\s*\*\*([^*]+)\*\*\s*:\s*(.+?)\s*$", line)
        if m:
            variables[m.group(1).strip()] = m.group(2).strip()
    return variables


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# a2: tabla de clases (libro de temas)
# --------------------------------------------------------------------------
def _canon_key(k: str) -> str:
    k = _strip_accents(k.strip().lower())
    k = re.sub(r"^n[oºro.\s]+", "", k)  # quitar prefijo "nº " / "nro "
    k = (k.replace("carácter/objetivo", "caracter")
           .replace("caracter/objetivo", "caracter")
           .replace("tema del día", "tema")
           .replace("eje temático", "eje_tematico"))
    return k.strip()


def parse_a2_table(path: Path) -> list[dict]:
    """Parsea la tabla Markdown de a2 -> lista de dicts con claves canónicas
    (clase, eje, eje_tematico, caracter, tema, actividades, fecha)."""
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
            continue  # fila separadora
        rows.append(dict(zip(header, cells)))
    return rows


def filter_class(rows: list[dict], clase, eje=None) -> list[dict]:
    out = []
    for r in rows:
        if str(r.get("clase", "")).strip() != str(clase).strip():
            continue
        if eje is not None and str(r.get("eje", "")).strip() != str(eje).strip():
            continue
        out.append(r)
    return out


# --------------------------------------------------------------------------
# Jinja2
# --------------------------------------------------------------------------
def make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(BASE_COMUN)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(env: Environment, template_rel: str, variables: dict) -> str:
    return env.get_template(template_rel).render(**variables)


# --------------------------------------------------------------------------
# LLM
# --------------------------------------------------------------------------
def load_client(config_llm_path: Path, provider=None, model_override=None):
    cfg = json.loads(config_llm_path.read_text(encoding="utf-8"))
    providers = cfg.get("provider", {})
    key = provider or cfg.get("default") or next(iter(providers))
    if key not in providers:
        raise SystemExit(f"Provider '{key}' no existe en config-llm.json")
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
        raise SystemExit(
            f"Falta API key para provider '{key}'. Cargala en config-llm.json o definí ZHIPU_API_KEY."
        )
    models = p.get("models", {})
    model = model_override or next(iter(models))
    disable_thinking = bool(p.get("disableThinking", False))
    return OpenAI(base_url=base_url, api_key=api_key), model, key, base_url, disable_thinking


def call_llm(client, model, prompt, disable_thinking=False, temperature=0.2, max_tokens=16384) -> str:
    extra_body = None
    if disable_thinking:
        # llama.cpp / Qwen3-style: apaga el reasoning.
        extra_body = {"chat_template_kwargs": {"enable_thinking": False}}
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
def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def nombre_ref(titulo: str) -> str:
    """Título del doc -> Nombre_Referencial: primera mayúscula + _, sin tildes."""
    s = _strip_accents(titulo).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "material"
    return s[0].upper() + s[1:]


def pascal(texto: str) -> str:
    palabras = re.split(r"[\s\-_]+", _strip_accents(texto))
    return "_".join(p.capitalize() for p in palabras if p)


def nombre_archivo(sigla, eje, sec, tema, tarea_code, nombre_referencial) -> str:
    codigo = f"{sigla}-{eje}{sec}"
    if tema is not None:
        codigo += str(tema)
    tarea_leg = TAREA_LEGIBLE.get(tarea_code, pascal(tarea_code))
    return f"{codigo}-{tarea_leg}-{nombre_referencial}.md"


def extraer_titulo(doc: str) -> str:
    for line in doc.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("# ").strip()
    for line in doc.splitlines():
        if line.strip():
            return line.strip()
    return "documento"


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
def write_output(path: Path, content: str):
    if path.exists():
        r = input(f"\nEl archivo '{path.name}' ya existe. ¿Sobrescribir? [S/n]: ").strip().lower()
        if r and r != "s":
            print("→ Se omite (no se sobrescribe).")
            return None
    path.write_text(content, encoding="utf-8")
    return path


def _find_latest(directory: Path, pattern: str):
    matches = sorted(Path(directory).glob(pattern))
    return matches[-1] if matches else None


# --------------------------------------------------------------------------
# Orquestación: a1 (plan anual) y a2 (plan de clases)
# --------------------------------------------------------------------------
def run_a1(args) -> list[tuple[str, str]]:
    materia_dir = MATERIAS / args.materia
    vars_cfg = parse_config_datos(materia_dir / "config-datos.md")
    contenidos = (materia_dir / "datos-contenidos_minimos.md").read_text(encoding="utf-8")
    variables = {
        **vars_cfg,
        "contenidos_minimos": contenidos,
        "Reglas_ciclo_lectivo": vars_cfg.get("Reglas_ciclo_lectivo", "(sin reglas adicionales)"),
        "Reglas_cuatrimestres": vars_cfg.get("Reglas_cuatrimestres", "(sin reglas adicionales)"),
    }
    env = make_env()
    client, model, pkey, base_url, dt = load_client(
        BASE_COMUN / "config-llm.json", args.provider, args.modelo
    )
    print(f"→ LLM: provider={pkey} model={model} @ {base_url}")
    prompt = render(env, TAREA_TEMPLATE["a1"], variables)
    if args.dry_run:
        print("\n--- PROMPT (dry-run, a1) ---\n" + prompt)
        return []
    print(f"\n=== a1 — Plan Anual de {args.materia} ===")
    doc = call_llm(client, model, prompt, dt)
    ref = nombre_ref(extraer_titulo(doc))
    fname = f"{args.materia}-Plan_Anual-{ref}.md"
    return [(fname, doc)] if write_output(OUTPUT / fname, doc) else []


def run_a2(args) -> list[tuple[str, str]]:
    materia_dir = MATERIAS / args.materia
    vars_cfg = parse_config_datos(materia_dir / "config-datos.md")
    contenidos = (materia_dir / "datos-contenidos_minimos.md").read_text(encoding="utf-8")

    # a2 depende de a1 (plan anual): ruta explícita o el más reciente en output/.
    a1_path = Path(args.a1) if args.a1 else _find_latest(OUTPUT, f"{args.materia}-Plan_Anual-*.md")
    if not a1_path or not a1_path.exists():
        raise SystemExit("No se encontró a1 (plan anual). Generá a1 primero o usá --a1 <ruta>.")

    variables = {
        **vars_cfg,
        "contenidos_minimos": contenidos,
        "planificacion_anual": a1_path.read_text(encoding="utf-8"),
    }
    env = make_env()
    client, model, pkey, base_url, dt = load_client(
        BASE_COMUN / "config-llm.json", args.provider, args.modelo
    )
    print(f"→ LLM: provider={pkey} model={model} @ {base_url}")
    print(f"→ Usando a1: {a1_path.name}")
    prompt = render(env, TAREA_TEMPLATE["a2"], variables)
    if args.dry_run:
        print("\n--- PROMPT (dry-run, a2) ---\n" + prompt)
        return []
    print(f"\n=== a2 — Plan de Clases (libro de temas) de {args.materia} ===")
    doc = call_llm(client, model, prompt, dt)
    titulo = extraer_titulo(doc)
    if titulo.startswith("|"):
        # a2 puede arrancar con la tabla (sin título "#"); usar un referencial estable.
        titulo = f"Libro de Temas {args.materia}"
    ref = nombre_ref(titulo)
    fname = f"{args.materia}-Plan_De_Clases-{ref}.md"
    return [(fname, doc)] if write_output(OUTPUT / fname, doc) else []


# --------------------------------------------------------------------------
# Orquestación: b1 (material didáctico)
# --------------------------------------------------------------------------
def run_b1(args) -> list[tuple[str, str]]:
    materia_dir = MATERIAS / args.materia
    if not materia_dir.exists():
        raise SystemExit(f"No existe la materia '{args.materia}' en {MATERIAS}")

    vars_cfg = parse_config_datos(materia_dir / "config-datos.md")

    # a2 (prerrequisito): ruta explícita, o el más reciente en output/, o ejemplo en la materia.
    if args.a2:
        a2_path = Path(args.a2)
    else:
        a2_path = _find_latest(OUTPUT, f"{args.materia}-Plan_De_Clases-*.md")
    if not a2_path or not a2_path.exists():
        a2_path = materia_dir / "ejemplo-planificacion_de_clases.md"
    if not a2_path.exists():
        raise SystemExit(f"No se encontró a2 (plan de clases). Generá a2 primero o usá --a2 <ruta>.")

    rows = parse_a2_table(a2_path)
    clase_rows = filter_class(rows, args.clase, args.eje)
    if not clase_rows:
        raise SystemExit(f"No se encontró la clase {args.clase} (eje {args.eje}) en {a2_path.name}")

    env = make_env()
    client, model, pkey, base_url, dt = load_client(
        BASE_COMUN / "config-llm.json", args.provider, args.modelo
    )
    print(f"→ LLM: provider={pkey} model={model} @ {base_url}")

    temas = [r.get("tema", "") for r in clase_rows]
    caracter = clase_rows[0].get("caracter", "")
    eje_tematico = clase_rows[0].get("eje_tematico", "")
    print(f"→ Clase {args.clase} (eje {args.eje}) — carácter: {caracter} | {len(temas)} tema(s)")

    resultados = []
    if args.por_tema:
        for i, tema in enumerate(temas, start=1):
            variables = {**vars_cfg, "caracter": caracter, "eje_tematico": eje_tematico, "temas": [tema]}
            prompt = render(env, TAREA_TEMPLATE["b1"], variables)
            if args.dry_run:
                print(f"\n--- PROMPT (dry-run, tema {i}) ---\n" + prompt)
                continue
            print(f"\n=== b1 clase {args.clase} tema {i}: {tema} ===")
            doc = call_llm(client, model, prompt, dt)
            ref = nombre_ref(extraer_titulo(doc))
            fname = nombre_archivo(args.materia, args.eje, args.clase, i, "b1", ref)
            if write_output(OUTPUT / fname, doc):
                resultados.append((fname, doc))
    else:
        variables = {**vars_cfg, "caracter": caracter, "eje_tematico": eje_tematico, "temas": temas}
        prompt = render(env, TAREA_TEMPLATE["b1"], variables)
        if args.dry_run:
            print("\n--- PROMPT (dry-run, combinado) ---\n" + prompt)
            return []
        print(f"\n=== b1 clase {args.clase} (combinado, {len(temas)} tema(s)) ===")
        doc = call_llm(client, model, prompt, dt)
        ref = nombre_ref(extraer_titulo(doc))
        fname = nombre_archivo(args.materia, args.eje, args.clase, None, "b1", ref)
        if write_output(OUTPUT / fname, doc):
            resultados.append((fname, doc))
    return resultados


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    # Windows: forzar UTF-8 en stdout/stderr para soportar acentos y símbolos (→).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="z-material-didactico (generador spec-driven)")
    ap.add_argument("--materia", required=True, help="sigla de materia (ej: IRI)")
    ap.add_argument("--tarea", default="b1", help="código de tarea (a1, a2, b1)")
    ap.add_argument("--clase", help="número de clase (requerido para b1)")
    ap.add_argument("--eje", help="número de eje (ej: 1)")
    ap.add_argument("--a2", help="ruta a un a2 (plan de clases) alternativo")
    ap.add_argument("--a1", help="ruta a un a1 (plan anual) alternativo")
    ap.add_argument("--provider", help="provider de config-llm.json (ej: glm-cloud)")
    ap.add_argument("--modelo", help="id de modelo (sobreescribe el del provider)")
    ap.add_argument("--por-tema", action="store_true", help="un material por tema (default: combinado)")
    ap.add_argument("--dry-run", action="store_true", help="arma y muestra el prompt sin llamar al LLM")
    args = ap.parse_args(argv)

    OUTPUT.mkdir(exist_ok=True)

    if args.tarea == "b1":
        if not args.clase:
            raise SystemExit("b1 requiere --clase (y preferentemente --eje).")
        docs = run_b1(args)
    elif args.tarea == "a1":
        docs = run_a1(args)
    elif args.tarea == "a2":
        docs = run_a2(args)
    else:
        raise SystemExit(f"Tarea '{args.tarea}' no implementada todavía.")
    print("\n=== Generados ===")
    for fname, _ in docs:
        print(" -", fname)


if __name__ == "__main__":
    main()
