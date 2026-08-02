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
output/                     ← generados (único global)
lote/                       ← lotes YAML (pendiente)
docs/                       ← referencia
main.py                     ← app
```

## 4. `a2` — Plan de Clases (8 columnas)

La tabla `a2` tiene **8 columnas permanentes**:

| id | Eje | nro_eje | nro_clase_eje | Carácter/Objetivo | Tema del Día | Actividades | Fecha |

- `nro_eje=0` → clase **sin dictado** (presentación, cierre, evaluación): `nro_clase_eje=0` siempre.
- `nro_eje` 1–4 → ejes con dictado; `nro_clase_eje` = secuencial dentro del eje.
- `b1` se alimenta de **Tema del Día + Actividades**.

## 5. Flujo de uso

```bash
# 1) Plan anual (a1) — insumo de a2
python main.py --materia IRI --tarea a1 --provider glm-cloud

# 2) Plan de clases / libro de temas (a2) — usa a1
python main.py --materia IRI --tarea a2 --provider glm-cloud

# 3) Material didáctico (b1) de una clase
python main.py --materia IRI --tarea b1 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia LPR --tarea b1 --eje 5 --clase-eje 1 --provider glm-cloud

# 4) Derivados (usan el b1 ya generado; mismo nombre referencial)
python main.py --materia IRI --tarea b2 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia IRI --tarea b3 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia IRI --tarea b4 --eje 1 --clase-eje 1 --provider glm-cloud
python main.py --materia IRI --tarea b5 --eje 1 --clase-eje 1 --provider glm-cloud
```

### Búsqueda de clase
- `--eje N --clase-eje M` (busca por `nro_eje` + `nro_clase_eje`).
- `--id N` (busca por `id` global; útil para eje 0).
- **eje 0 → skip automático** (no genera tipo b).

### Flags
| Flag | Descripción |
|---|---|
| `--materia <sigla>` | Obligatorio (ej. IRI; se normaliza a MAYÚSCULAS en el naming) |
| `--tarea <código>` | a1, a2, b1, b2, b3, b4, b5 |
| `--eje <n>` | nro_eje |
| `--clase-eje <n>` | nro_clase_eje |
| `--id <n>` | id global (alternativa a --eje/--clase-eje) |
| `--a2 <ruta>` | a2 alternativo (si no, busca el más reciente en output/) |
| `--a1 <ruta>` | a1 alternativo (para a2) |
| `--provider <key>` | provider de config-llm.json |
| `--modelo <id>` | sobreescribe el modelo |
| `--dry-run` | arma y muestra el prompt sin llamar al LLM |

## 6. Naming de salida

`<sigla>-<nro_eje><nro_clase_eje>-<Tarea_PascalCase>-<nombre_≤50>.md`

Ej.: `IRI-11-Material_Didactico-Fundamentos_de_redes_de_area.md`

El **nombre referencial** lo genera el LLM en `b1` (del título); `b2`–`b5` lo **reutilizan** (mismo nombre para toda la clase).

## 7. Output

- Único global en `output/`.
- Si el archivo existe → **pregunta** "¿Sobrescribir? [S/n]" (default Sí).
- Al final imprime el **tiempo insumido** (`⏱  Xs`).

## 8. Dependencias entre tareas (DAG)

```
a1 → a2 → b1 → b2, b3, b5
              b2 → b4
```

- `b2`, `b3`, `b5` requieren que `b1` exista (usan su contenido como insumo).
- `b4` requiere que `b2` exista.
- **Cascada automática** (b1 → b2,b3,b5) y **lote YAML**: pendientes de implementar.

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

- DAG con cascada (b1 → b2,b3,b5 automático).
- Lote YAML (`lote/*.yaml`).
- Plantillas c1, c2, d1, d2 (evaluación e integradora).
- Fusión de documentos (b3+b4 para imprimir).
