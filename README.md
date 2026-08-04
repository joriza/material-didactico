# z-material-didactico

Generador de **material didáctico técnico** a partir de una planificación de clases, usando un LLM (GLM/Z.ai en la nube o llama.cpp local). Arquitectura **spec-driven** de 3 capas: las reglas viven en plantillas (Jinja2), no en el código. Agregar o modificar tareas no requiere tocar `main.py`.

Las decisiones de arquitectura están en [`design.md`](./design.md). Las reglas pedagógicas/formato en [`base-comun/specificacion-principal.md`](./base-comun/specificacion-principal.md).

---

## 1. Requisitos

- **Python ≥ 3.10**
- Dependencias: `openai`, `jinja2`, `pyyaml` (`pip install -r requirements.txt`)
- Un servidor LLM **OpenAI-compatible**:
  - Cloud: GLM/Z.ai Coding Plan (`https://api.z.ai/api/coding/paas/v4`) con API key, o
  - Local: `llama.cpp` en `http://localhost:8080/v1`.

## 2. Instalación

```bash
pip install -r requirements.txt
```

Configurar `base-comun/config-llm.json` (copiar de `config-llm.example.json` y pegar tu API key):

```json
{
  "default": "glm-cloud",
  "provider": {
    "glm-cloud": {
      "options": {
        "baseURL": "https://api.z.ai/api/coding/paas/v4",
        "apiKey": "TU_API_KEY"
      },
      "models": { "glm-4.7": { "name": "glm-4.7" } }
    }
  }
}
```

> `config-llm.json` está en `.gitignore` (no se commitea). El `example` sí.

## 3. Estructura

```
base-comun/                 ← común a todas las materias
  specificacion-principal.md   base Jinja2 (reglas pedagógicas)
  config-llm.json              LLM (API key, gitignored)
  tareas.yaml                  manifiesto (jerarquía + dependencias)
  tareas/                      plantillas de tarea (Jinja2)
materias/<sigla>/           ← datos por materia (sueltos)
  config-datos.md
  datos-contenidos_minimos.md
output/                     ← generados (.md + .csv de tablas a1/a2; único global)
docs/                       ← referencia
main.py                     ← app
```

### 3.1 Origen de `datos-contenidos_minimos.md`

El archivo `materias/<sigla>/datos-contenidos_minimos.md` es la **fuente de verdad del alcance de cada materia**: lo consume `a1` y `a2` como insumo a organizar, y `b1` como contexto de desambiguación. El origen del contenido varía por materia:

| Materia(s) | Origen | Notas |
|---|---|---|
| EIN, IRI, ITI-PDA, PDISC | Temario oficial (diseño curricular) | Estructurados en `### N.` + viñetas |
| LPR | Temario oficial **+ adenda institucional** | Línea explícita "Se establece que el lenguaje de programación a utilizar es Python" (no está en el diseño curricular original) |
| LSO | Temario oficial **refactorizado y concretado a tecnología** | Reescrito a C#/.NET + Minimal APIs + SQL Server + EF Core (commits `49f777e`, `656deec`) |

### 3.2 Agregar o renombrar una materia

Hay **dos operaciones distintas** con cuidados muy diferentes. No las mezcles.

> **`Variable_Materia` ≠ sigla** — el error #1 al renombrar.
> - `Variable_Materia` (en `config-datos.md`) es el **nombre largo** (ej. `"ELECTRÓNICA INDUSTRIAL"`). Solo lo consumen las plantillas Jinja2 para imprimir headers/contenido. NO afecta naming ni lookups.
> - La **sigla** (`--materia EIN`) determina el nombre de la carpeta (`materias/EIN/`) y el prefijo de todos los outputs (`EIN-*.md`). SÍ afecta naming y lookups.

#### 3.2.1 Cambiar el nombre largo (`Variable_Materia`)

Editás solo `materias/<SIGLA>/config-datos.md`, línea `Variable_Materia: <nombre largo>`.

- **Afecta**: contenido de los outputs (headers `Materia: ...` en b1/b2/b6, menciones en el cuerpo).
- **NO afecta**: naming de archivos, lookups, cascada, `.bat`.
- **Cuidado**: los `.md` ya generados conservan el viejo `Variable_Materia`. Regeneralos para que reflejen el nuevo nombre.

#### 3.2.2 Cambiar la sigla (`--materia <SIGLA>`)

La sigla está "bakeada" en varios lugares. Aparece en:

1. **Carpeta** `materias/<SIGLA>/`
2. **Outputs previos**: prefijo `output/<SIGLA>-*.md`. La app busca prerrequisitos por ese prefijo (`main.py:390, 514`).
3. **Scripts `.bat`** (`grupo1.bat`, `grupo2.bat`): invocan `--materia <SIGLA>`.
4. **Documentación** (README, `design.md`): menciones ejemplares; no funcionales.

**Cuidados clave**:

- **Mayúsculas obligatorias**: `main.py:496` normaliza con `.upper()`. La carpeta va en MAYÚSCULAS (`EIN`, no `ein`).
- **Outputs previos quedan huérfanos**: la app NO migra automáticamente. Renombrá `output/<VIEJO>-*.md` → `output/<NUEVO>-*.md` para preservar trabajo, o regenerá desde cero.
- **La sigla NO va en `config-datos.md`**: ese archivo lleva `Variable_Materia` (nombre largo), no la sigla.
- **Siglas con guion** (ej. `ITI-PDA`): funcionan, pero el naming visual se parsea peor (`ITI-PDA-XX-...md`). Preferí siglas sin guion cuando sea posible.

**Checklist — renombrar sigla**:

```
1. Renombrar carpeta: materias/<VIEJO>/ → materias/<NUEVO>/
2. Renombrar outputs:  output/<VIEJO>-*.md → output/<NUEVO>-*.md
3. Actualizar --materia en los .bat
4. (Opcional) Actualizar ejemplos en README / design.md
5. Smoke test: python main.py --materia <NUEVO> --tarea a1 --dry-run
```

**Checklist — agregar materia nueva** (más común):

```
1. Crear carpeta materias/<SIGLA>/ en MAYÚSCULAS
2. Copiar y editar config-datos.md desde otra materia
3. Crear datos-contenidos_minimos.md (origen según §3.1)
4. (Opcional) Agregar invocación a un .bat
5. Primera corrida con --tarea a1
```

> **Marcador `@validar` en plantillas**: las plantillas pueden declarar validación de longitud con un comentario Jinja `{# @validar: doc_entero min=20000 #}` (medida + `min`/`max`). La app lo lee de la plantilla cruda y **avisa** (no bloquea) si el output no cumple. Jinja descarta el comentario, así que no contamina el prompt. Medidas: `doc_entero` (todo el doc) y `parrafo_sintesis` (primer párrafo sustantivo).

## 4. `a2` — Plan de Clases (9 columnas)

La tabla `a2` tiene **9 columnas permanentes** (orden exacto):

| id | Eje | nro_eje | nro_clase_eje | Tema_Nro | Carácter/Objetivo | Tema del Día | Actividades | Fecha |

- `nro_eje=0` → clase **sin dictado** (presentación, cierre, evaluación): `nro_clase_eje=0` siempre.
- `nro_eje` 1–4 → ejes con dictado; `nro_clase_eje` = secuencial dentro del eje.
- `Tema_Nro` → número del tema **dentro del encuentro** (`1` mono-tema; `1`, `2`, excepcionalmente `3` multi-tema). Un encuentro con varias filas comparte `id`+`nro_eje`+`nro_clase_eje` y solo varía `Tema_Nro`+`Tema del Día`. Detalle en `design.md §4.3`.
- `b1` se alimenta de **Tema del Día + Actividades**.

## 5. Flujo de uso

```bash
# 1) Plan anual (a1) — insumo de a2
python main.py --materia IRI --tarea a1 --provider glm-cloud

# 2) Plan de clases / libro de temas (a2) — usa a1
python main.py --materia IRI --tarea a2 --provider glm-cloud

# 3) Detalle de encuentros (a3) — usa a1+a2; SIN restricciones de longitud
#    Opcional pero recomendado: alimenta b1 con detalle y fundamentos previos
python main.py --materia IRI --tarea a3 --provider glm-cloud

# 4) Material didáctico (b1) de una clase — usa a3 si existe (sino, fallback a a2)
python main.py --materia IRI --tarea b1 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia LPR --tarea b1 --eje 5 --clase-eje 1 --provider glm-cloud

# 5) Derivados (usan el b1 ya generado; mismo nombre referencial)
python main.py --materia IRI --tarea b2 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia IRI --tarea b4 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia IRI --tarea b5 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia IRI --tarea b6 --eje 1 --clase-eje 1 --provider glm-cloud

# 6) Todos los ejes con dictado (sin --eje → toda la materia)
python main.py --materia IRI --tarea b1 --provider glm-cloud  # sin --eje → todos los ejes con dictado
```

> **CSV de tablas**: `a1` y `a2` generan además `<mismo-basename>.csv` (UTF-8 con BOM para Excel) con la tabla parseada. El `.csv` de `a1` sanea celdas ricas (`<br>` → salto de línea, se elimina `**bold**` y `` `code` ``); el de `a2` pasa las celdas atómicas tal cual.

### Búsqueda de clase

La selección de clase sigue una jerarquía de especificidad (de más a menos):

| Invocación | Alcance |
|---|---|
| `--id N` | Una clase por id global |
| `--eje N --clase-eje M` | Una clase puntual |
| `--eje N` | Todas las clases del eje N |
| (sin flags) | Todos los ejes con dictado |

- `--eje N --clase-eje M` (busca por `nro_eje` + `nro_clase_eje`).
- `--id N` (busca por `id` global; útil para eje 0).
- **eje 0 → skip automático** (no genera tipo b).

### Flags
| Flag | Descripción |
|---|---|
| `--materia <sigla>` | Obligatorio (ej. IRI; se normaliza a MAYÚSCULAS en el naming) |
| `--tarea <código>` | a1, a2, a3, b1, b2, b4, b5, b6 |
| `--eje <n>` | nro_eje |
| `--clase-eje <n>` | nro_clase_eje |
| `--id <n>` | id global (alternativa a --eje/--clase-eje) |
| `--tema-idx <n>` | Tema_Nro puntual dentro del encuentro (multi-tema). Si se omite, procesa todos los temas. |
| `--a2 <ruta>` | a2 alternativo (si no, busca el más reciente en output/) |
| `--a1 <ruta>` | a1 alternativo (para a2 y a3) |
| `--a3 <ruta>` | a3 alternativo (para b1 y derivados; si no se pasa, se usa el más reciente en output/) |
| `--provider <key>` | provider de config-llm.json |
| `--modelo <id>` | sobreescribe el modelo |
| `--dry-run` | arma y muestra el prompt sin llamar al LLM |

## 6. Naming de salida

`<sigla>-<nro_eje><nro_clase_eje>-<Tarea_PascalCase>-<nombre_≤50>.md`

Ej.: `IRI-11-Material_Didactico-Fundamentos_de_redes_de_area.md`

**a-tasks** (naming fijo, sin `nro_eje`/`nro_clase_eje`):
- `a1`: `<sigla>-Plan_Anual-Ciclo_lectivo.md`
- `a2`: `<sigla>-Plan_De_Clases-Libro_de_temas.md`
- `a3`: `<sigla>-Detalle_Encuentros-Curso_completo.md`

**CSV de tablas** (a1, a2): mismo basename que el `.md`, extensión `.csv`.
Ej.: `IRI-Plan_Anual-Ciclo_lectivo.csv`, `IRI-Plan_De_Clases-Libro_de_temas.csv`.

El **nombre referencial** lo genera el LLM en `b1` (del título); `b2`, `b4`, `b5` y `b6` lo **reutilizan** (mismo nombre para toda la clase/tema).

## 7. Output

- Único global en `output/`.
- **a-tasks (a1, a2, a3)**: si el `.md` existe, pregunta **antes de llamar al LLM** "¿Regenerar (gasta tokens)? [s/N]" (default No → **cero tokens** si se conserva). Si se conserva el `.md` y falta el `.csv` (a1, a2), lo genera del `.md` existente sin llamar al LLM.
- **b-tasks**: si el `.md` existe, pregunta al escribir "¿Sobrescribir? [S/n]" (default Sí; el LLM ya corrió).
- **CSV de tablas** (a1, a2): se generan junto con el `.md`. Si el `.csv` ya existe y el `.md` se conserva, **no se modifica** (lo cuida el usuario; para refrescarlo, borrarlo y volver a correr).
- Al final imprime el **tiempo insumido** (`⏱  Xs`).

## 8. Dependencias entre tareas (DAG)

```
a1 → a2 → a3 → b1 → b2, b5, b6
                  b2 → b4
```

- `a3` es **opcional** como prerrequisito de `b1`: si existe, alimenta `b1` con detalle del encuentro y fundamentos previos desarrollados. Si no existe, `b1` cae a solo `a2` (backward compatibility).
- `b2`, `b5`, `b6` requieren que `b1` exista (usan su contenido como insumo).
- `b4` requiere que `b2` exista.
- **Cascada B bidireccional implementada** (`resolver_cascada_b`): pedir una tarea tipo b → genera prerrequisitos + dependientes automáticamente. **Modo multi-eje** implementado: sin `--eje`, procesa todos los ejes con dictado.

## 9. Troubleshooting

| Síntoma | Solución |
|---|---|
| `Falta API key` | Pegar la key en `base-comun/config-llm.json` o definir `ZHIPU_API_KEY` |
| `No se encontró a2` | Generar primero `--tarea a2` (o usar `--a2 <ruta>`) |
| `No se encontró output de b1` | Generar primero `--tarea b1` (b2-b5 dependen de b1) |
| `nro_eje=0 → no se generan tipo b` | Comportamiento correcto: las clases sin dictado no tienen material |
| Caracteres raros en consola (Windows) | `main.py` fuerza UTF-8; si persiste, usar terminal moderna |

## 10. Conversión a PDF

El script `convert.ps1` (PowerShell 5.1+) convierte todos los `.md` de una carpeta a PDF, con detección automática del motor disponible.

### Requisitos

Instalá uno de estos (recomendado primero):

```powershell
# Opción A — Chocolatey
choco install pandoc wkhtmltopdf

# Opción B — descargas directas:
#   Pandoc:      https://pandoc.org/installing.html
#   wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
```

> En Windows, después de instalar, **reiniciá la terminal** para que el PATH se actualice.

### Uso

```powershell
# Desde la raíz del repo (siempre):
.\convert.ps1                                        # convierte ./  (carpeta actual)
.\convert.ps1 -Path output                           # convierte output/
.\convert.ps1 -Path output\tmp02 -Css .\assets\print.css -Force
.\convert.ps1 -Path output\PIRI -Css .\assets\print.css 

.\convert.ps1 -Path output\IRI-auto -Css .\assets\print.css -Force
.\convert.ps1 -NoFooter                              # sin numeración al pie
```

El script autodetecta el motor en este orden de preferencia:
1. `pandoc + xelatex` (mejor calidad tipográfica; no soporta CSS).
2. `pandoc + wkhtmltopdf` (decente, soporta CSS y footer con página/total).
3. `md-to-pdf` (Node + Chromium; soporta CSS, footer requiere config extra).
4. `markdown-pdf` (Node; soporta CSS).

### Parámetros

| Parámetro | Default | Descripción |
|---|---|---|
| `-Path` | `.` (CWD) | Carpeta con los `.md` a convertir. |
| `-Css` | — | Archivo `.css` de estilos. Solo motores HTML. |
| `-NoFooter` | — | Desactiva el pie con `nro / total` (solo `pandoc-wkhtmltopdf`). |
| `-PageSize` | `A4` | Tamaño de página (`A4`, `Letter`, `Legal`, `A3`, etc.). |
| `-Engine` | autodetecta | `pandoc-xelatex` \| `pandoc-wkhtmltopdf` \| `md-to-pdf` \| `markdown-pdf`. |
| `-Force` | — | Regenera los PDFs que ya existen (por defecto los salta). |

### Footer con numeración y cabecera con nombre de archivo

Con `pandoc + wkhtmltopdf` (motor recomendado):

- **Cabecera centrada**: nombre del archivo (sin extensión), fuente 8pt, separada por línea.
- **Pie centrado**: `[page] / [topage]` (ej. `3 / 12`), fuente 8pt, separado por línea.

El pie se puede desactivar con `-NoFooter`. La cabecera siempre va (es la identificación del documento al imprimir).

> wkhtmltopdf no soporta los CSS paged media (`counter(page)`), por eso se usan las variables nativas `[page]` y `[topage]` pasadas vía `--pdf-engine-opt`.

### Márgenes y tipografía

Los márgenes y tamaño de letra se controlan en dos lugares:

- **Script** (`convert.ps1`): márgenes de página (top/bottom 20mm, laterales 10mm) pasados vía `-V margin-*` a pandoc.
- **CSS** (`assets/print.css` o el que pases con `-Css`): tipografía (`body { font-size: 12pt }`), encabezados, tablas, código.

Editá el CSS para cambiar fuentes/colores/espaciados. Editá el script solo si querés cambiar los márgenes de página.

### CSS base

`assets/print.css` es un punto de partida: A4, Arial 11pt, encabezados azul institucional, tablas con bordes y zebra, código en Consolas, salto de página entre `h1` (excepto el primero). Editalo libremente o pasá tu propio CSS con `-Css <ruta>`.

### Códigos de salida

| Código | Significado |
|---|---|
| `0` | Éxito. |
| `1` | Carpeta inexistente. |
| `2` | Ningún motor disponible (mensaje instructivo incluido). |
| `3` | Algunos archivos fallaron. |

## 11. Pendiente

- (Sin pendientes)

## 12. Mensajes de commit (Conventional Commits)

Los commits usan el estándar **Conventional Commits**: un prefijo antes de los dos puntos indica el *tipo* de cambio. Facilita la lectura del historial y la generación automática de CHANGELOG/versionado.

Prefijos usados en este repo:

| Prefijo | Uso | Ejemplo del historial |
|---|---|---|
| `feat` | Nueva funcionalidad (algo que hace cosas nuevas para el usuario) | `feat: modo multi-eje, cascada R1+R2...` |
| `fix` | Corrección de un bug (algo que no funciona como debería) | `fix: sigla de materia siempre en mayusculas...` |
| `chore` | Mantenimiento que no es feature ni fix: config, metadatos, scripts, sincronizar docs con código | `chore: sincroniza metadata y config...` |
| `docs` | Cambios **solo** en documentación (`.md`) | `docs: contenidos minimos LSO...` |

**Regla práctica:** si el cambio *agrega capacidad* que el usuario nota → `feat`; si *corrige* algo roto → `fix`; si es *mantenimiento* (config, metadatos, scripts) → `chore`; si tocás *solo `.md`* → `docs`.

El cuerpo del commit (opcional, tras un salto de línea o un segundo `-m`) explica el *qué* y el *por qué*, idealmente con viñetas cuando hay varios puntos. El prefijo solo clasifica.

> El estándar completo incluye más prefijos (`style`, `refactor`, `perf`, `test`, `build`, `ci`, `revert`), pero en este repo se usan principalmente los cuatro de la tabla.
