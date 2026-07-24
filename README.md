# z-material-didactico

Generador de **material didáctico técnico** a partir de un listado de temas, usando un LLM (local vía `llama.cpp` o en la nube vía GLM/Z.ai). Cada tema genera un documento Markdown de estudio, finalizado y autosuficiente, con su sección de síntesis y métricas de lectura.

Las reglas pedagógicas y de formato están en [`spec-princ.md`](./spec-princ.md). Este README explica cómo instalar, configurar y usar la aplicación.

---

## 1. Requisitos

- **Node.js ≥ 20** (probado con Node 25).
- Un servidor LLM **OpenAI-compatible** accesible:
  - Local: `llama.cpp` (por defecto en `http://localhost:8080/v1`), o
  - Cloud: GLM/Z.ai Coding Plan (`https://api.z.ai/api/coding/paas/v4`) con API key.

Verificá con `node --version`.

---

## 2. Instalación

Desde la raíz del proyecto:

```bash
npm install
```

Dependencias: `ai`, `@ai-sdk/openai-compatible`, `commander`. No requiere paso de build (JavaScript, ESM nativo).

---

## 3. Archivos de configuración

### 3.1 `config-datos.md` — contexto institucional y pedagógico

Variables en formato `- **Clave**: valor`. Obligatorias:

```
- **Variable_Establecimiento**: EEST Nº 3
- **Variable_Materia**: INSTALACIÓN, MANTENIMIENTO Y REPARACIÓN DE REDES INFORMÁTICAS
- **Variable_Carrera**: TÉCNICO EN INFORMÁTICA PROFESIONAL Y PERSONAL
- **Variable_Curso**: 7mo. 2da.
- **Variable_Docente**: Izaguirre Jorge
```

Otros campos (carga horaria, cantidad de ejes/clases) se ignoran en la generación.

### 3.2 `config-llm.json` — proveedores y modelos

Define uno o más proveedores. Ejemplo con `llama.cpp` local y GLM cloud:

```json
{
  "default": "llama-cpp",
  "provider": {
    "llama-cpp": {
      "name": "llama-cpp",
      "disableThinking": true,
      "options": {
        "baseURL": "http://localhost:8080/v1",
        "apiKey": "dummy-key"
      },
      "models": {
        "local-model": { "name": "local-model" }
      }
    },
    "glm-cloud": {
      "name": "glm-cloud",
      "options": {
        "baseURL": "https://api.z.ai/api/coding/paas/v4",
        "apiKey": "PEGA_TU_KEY_AQUI"
      },
      "models": {
        "glm-4.7": { "name": "glm-4.7" }
      }
    }
  }
}
```

- `default`: proveedor usado si no se pasa `--provider`.
- `disableThinking: true`: solo para `llama.cpp` con modelos de razonamiento (Qwen3-style). Inyecta `chat_template_kwargs.enable_thinking=false` para que la respuesta vaya en `content`. **No aplicar a GLM cloud.**
- `apiKey`: obligatoria para proveedores en la nube. Si se deja vacía, se intenta leer de la variable de entorno `ZHIPU_API_KEY`. Para servidores locales (`localhost`/`127.0.0.1`) se usa `dummy-key` automáticamente.

#### ⚠ Cómo se elige el modelo (importante)

El **id de modelo enviado al endpoint** se resuelve así:

1. Si pasás `--modelo <id>` por CLI → usa ese id.
2. Si no → usa la **CLAVE** del primer modelo declarado en `models` (el campo entre comillas antes de los dos puntos).
3. El campo `name` interno (`"name": "..."`) **NO se usa** para el id enviado; es solo metadata.

Ejemplo problemático:

```json
"models": { "glm-4.7": { "name": "glm-4.5-flash" } }
```

Acá la app envía **`glm-4.7`** (la clave), **no** `glm-4.5-flash`. Para usar `glm-4.5-flash` hay dos formas:

- Cambiar la **clave**: `"models": { "glm-4.5-flash": { "name": "glm-4.5-flash" } }`, o
- Pasarlo por CLI: `--modelo glm-4.5-flash`.

### 3.3 `temas-a-tratar.md` — insumo principal (una fila = un documento)

Cada **fila no vacía** (que no empiece con `#`) corresponde a **un documento Markdown de salida**.

```
Seguridad y EPP. Identificación de riesgos.
Prevención Técnica. Simulacro de uso de EPP.
Nivelación Lógica. Resolución de problemas.
Taller de Nivelación. Prácticas de laboratorio.
Redes LAN y Topología. Análisis de diseños físicos.
```

El número de fila (en orden, desde 1) forma parte del nombre del archivo de salida.

### 3.4 `marcos/` — modo legacy (opcional)

Para generar una clase con metadatos ricos (eje temático, repaso, contexto adicional), usá un archivo `marcos/clase-XX.md` y el flag `--marco`. Ver [`marcos/clase-12.md`](./marcos/clase-12.md) como ejemplo. Es un modo alternativo al de `temas-a-tratar.md`.

---

## 4. Uso

### 4.1 Comando base

```bash
npm run gen -- <flags>
# o directamente:
node src/index.js <flags>
```

### 4.2 Modos (elegir uno obligatoriamente)

| Modo | Flag | Qué hace |
|------|------|----------|
| **Fila** | `--fila <n>` | Genera el documento de la fila `n` de `temas-a-tratar.md`. |
| **Todas** | `--todas` | Genera un documento por cada fila (uno a uno, secuencial). |
| **Marco** | `-m, --marco <id\|path>` | Modo legacy: usa `marcos/clase-<id>.md` (o la ruta indicada). |

Si no se especifica ninguno, la app muestra error pidiendo un modo.

### 4.3 Flags generales

| Flag | Default | Descripción |
|------|---------|-------------|
| `-p, --provider <key>` | `default` del JSON | Proveedor a usar (`llama-cpp`, `glm-cloud`). |
| `--modelo <id>` | clave del 1er modelo | Sobreescribe el id de modelo enviado al endpoint. |
| `--temas <path>` | `temas-a-tratar.md` | Ruta al archivo de temas. |
| `--config-datos <path>` | `config-datos.md` | Ruta al config institucional. |
| `--config-llm <path>` | `config-llm.json` | Ruta al config de proveedores. |
| `--minimo <n>` | `4000` | Mínimo de caracteres del documento (**20000 en producción**, ver spec §4.2). |
| `--reintentos <n>` | `2` | Reintentos de continuación si queda corto del mínimo. |
| `--max-tokens <n>` | `16384` | Tokens máximos por llamada. |
| `--temperature <n>` | `0.2` | Temperatura de muestreo (texto técnico: baja). |
| `--dry-run` | off | Arma y muestra el prompt sin llamar al LLM (valida config). |
| `--sin-sintesis` | off | Omite la segunda llamada de síntesis. |

### 4.4 Ejemplos

```bash
# Generar el documento de la fila 1 con GLM cloud (calidad)
npm run gen -- --fila 1 -p glm-cloud --minimo 20000

# Generar todos los documentos (uno por fila de temas-a-tratar.md)
npm run gen -- --todas -p glm-cloud --minimo 20000

# Validar config y ver el prompt sin gastar tokens
npm run gen -- --fila 1 -p glm-cloud --dry-run

# Probar otro modelo sin tocar el JSON
npm run gen -- --fila 1 -p glm-cloud --modelo glm-4.5-flash --minimo 15000

# Modo legacy con marco
npm run gen -- --marco 12 -p glm-cloud

# Modelo local (llama.cpp debe estar corriendo en :8080)
npm run gen -- --fila 1
```

> El stream del LLM se imprime en vivo en la consola. Para producción (`--minimo 20000`) cada documento puede tardar varios minutos.

---

## 5. Salida

- **Ubicación:** siempre en la carpeta `output/` del proyecto.
- **Nombre:** `<número de fila>-<nombre-corto-referencial>.md` (ej.: `1-seguridad-y-epp-identificacion-de-riesgos.md`). El slug se deriva del tema de la fila, en minúsculas y sin acentos.
- **Estructura del archivo:**
  1. Documento principal (título, temas, módulos, casos prácticos).
  2. Separador `<!-- z-material-didactico: sintesis-y-conclusion -->`.
  3. Sección **Síntesis y Conclusión** con conteos **exactos** (calculados por la app, no por el LLM): caracteres del informe, síntesis global (una oración), 5 puntos clave y tiempos estimados de lectura continua/activa.

---

## 6. Validaciones automáticas

Al generar, la app revisa:

- **Longitud mínima** de caracteres (avisa si quedó corta).
- **Ausencia de LaTeX** (`$...$`, `\frac`, `\(...\)`, etc.).
- **Número de clase/sesión** en el texto (se ignoran falsos positivos de categorías normativas como *chaleco clase 3*, *extintor clase A*).
- **Cierres dubitativos/interactivos** (heurístico).

Los avisos se listan al final de cada generación; no bloquean la escritura del archivo.

---

## 7. Modelo recomendado

| Modelo | Cuándo | Notas |
|--------|--------|-------|
| **`glm-4.7`** (GLM Coding Plan) | **Recomendado para producción** | Calidad técnica alta y correcta; genera 20k+ caracteres en una sola llamada; gratis en el coding plan. |
| `glm-4.5-flash` | Solo pruebas rápidas | Más rápido, pero con menor rigor y algunos glitches (errores conceptuales, typos). |
| Modelo local (`llama.cpp`) | Sin conexión / pruebas | Depende del modelo cargado. Los modelos chicos de razonamiento producen texto repetitivo y con errores conceptuales; usar uno ≥ 7B-9B instruct para calidad. |

---

## 8. Resolución de problemas

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| `401 token expired or incorrect` | API key vacía o incorrecta | Pegarla en `config-llm.json` → `provider.<key>.options.apiKey`, o definir `ZHIPU_API_KEY`. |
| `401` en endpoint de coding | `baseURL` equivocado | Para Coding Plan usar `https://api.z.ai/api/coding/paas/v4` (no el general). |
| `429 余额不足` (saldo) | Cuenta sin saldo en el endpoint general | Usar el endpoint de Coding Plan o recargar saldo en `open.bigmodel.cn`. |
| `terminated` / stream sin texto | Modelo de razonamiento local sin `disableThinking` | Agregar `"disableThinking": true` al provider `llama-cpp` en el JSON. |
| Documento se corta antes del mínimo | `max_tokens` bajo | Subir `--max-tokens` (ej. 16384); el anti-recorte continúa automáticamente. |
| Usa un modelo distinto al esperado | Confusión clave vs `name` | El id enviado es la **clave** del JSON o `--modelo`. Ver sección 3.2. |

Para ver el stack completo de un error: `DEBUG=1 node src/index.js ...`.

---

## 9. Referencias

- Especificación funcional y pedagógica: [`spec-princ.md`](./spec-princ.md).
- Prompt base histórico: [`spec-mat-did.md`](./spec-mat-did.md).
- Ejemplo de marco (modo legacy): [`marcos/clase-12.md`](./marcos/clase-12.md).
