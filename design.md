# Diseño del sistema — z-material-didactico

Documento de arquitectura. Fuente única de las decisiones de diseño. Las reglas pedagógicas/formato viven en `base-comun/specificacion-principal.md`; este archivo describe la **arquitectura** de la app.

---

## 1. Stack

- **Python ≥ 3.10** + **Jinja2** (plantillas con herencia) + **PyYAML** (lotes y manifiesto) + lib **`openai`** (streaming, OpenAI-compatible).
- Un solo entrypoint: `main.py`. Sin frameworks.
- Windows: `main.py` fuerza `sys.stdout.reconfigure(encoding="utf-8")` para soportar acentos y símbolos.

## 2. Capas (3 niveles de variación)

| Capa | Variación | Dónde |
|---|---|---|
| **Común** | No varía | `base-comun/specificacion-principal.md`, `config-llm.json`, `tareas/`, `tareas.yaml` |
| **Tareas** | Por tipo de tarea; **iguales para toda materia** | `base-comun/tareas/tarea-*.md` (plantillas Jinja2) |
| **Datos auxiliares** | Por materia; intercambiables | `materias/<sigla>/*.md` (sueltos) |

Las tareas **heredan** la capa común (Jinja2 `{% extends %}`). Los datos rellenan los placeholders.

## 3. Estructura de carpetas

```
z-material-didactico/
├── base-comun/
│   ├── specificacion-principal.md      ← capa común (base Jinja2 con {% block tarea %})
│   ├── config-llm.json                 ← LLM común (gitignored; NO se commitea)
│   ├── config-llm.example.json         ← plantilla sin API key (commiteada)
│   ├── tareas.yaml                     ← manifiesto (jerarquía + dependencias + vocabulario Caracter)
│   └── tareas/                         ← plantillas de tarea (comunes a toda materia)
│       ├── tarea-plan_anual.md         (a1)
│       ├── tarea-plan_de_clases.md     (a2)
│       ├── tarea-material_didactico.md (b1)
│       ├── tarea-actividad_aulica.md   (b2)
│       ├── tarea-sintesis_material.md  (b3)
│       ├── tarea-respuestas_actividad_aulica.md (b4)
│       └── tarea-planificacion_aulica.md (b5)
├── materias/
│   └── IRI/                            ← Redes (datos sueltos)
│       ├── config-datos.md
│       └── datos-contenidos_minimos.md
├── lote/                               ← lotes YAML (pendiente de implementar)
├── output/                             ← output único global (naming ordena por materia)
├── docs/                               ← referencia (14-Pt-Mat+Activ+sint.md)
├── design.md                           ← este documento
├── main.py                             ← app
└── requirements.txt                    ← openai, jinja2, pyyaml
```

## 4. `a2` — Plan de Clases (Libro de Temas)

### 4.1 Definición PERMANENTE y ÚNICA de columnas

La tabla `a2` tiene **8 columnas en este orden exacto** (no hay versión alternativa):

| id | Eje | nro_eje | nro_clase_eje | Carácter/Objetivo | Tema del Día | Actividades | Fecha |
|---|---|---|---|---|---|---|---|

- **`id`**: número secuencial global, comenzando en 1. Debe llegar hasta `Cantidad_clases`. Sirve como log y para identificar filas únicas.
- **`Eje`**: nombre/descripción del Eje temático (texto, ej. "Fundamentos de Redes…").
- **`nro_eje`**: número del eje. `0` para clases **sin dictado** (presentación, diagnóstico, cierre, evaluación, intensificación); `1` a `Cantidad_ejes` para ejes con dictado.
- **`nro_clase_eje`**: número secuencial de la clase **dentro del eje**. **Si `nro_eje=0`, entonces `nro_clase_eje=0` siempre.**
- **`Carácter/Objetivo`**: selección obligatoria del vocabulario controlado.
- **`Tema del Día`**: descripción sintética del contenido (es lo que `b1` desarrolla).
- **`Actividades`**: acciones pedagógicas.
- **`Fecha`**: la coloca el docente manualmente (no se estima).

### 4.2 Restricciones (indicaciones al LLM en la plantilla `a2`)

- Ningún campo debe exceder los `Char_campos` (35) caracteres.
- `nro_eje` ∈ {0} ∪ [1, `Cantidad_ejes`]. Ejes con dictado ≤ 4.
- Carácter/Objetivo del vocabulario: Presentación, Diagnóstico, Teórica, Práctica, Teórico-Práctica, Dialogada, Reflexiva, Aplicación, Argumentativa, Evaluativa, Evaluativa (en proceso o final), Experimental, Fijación, Informativa, Integración, Interpretativa, Investigación, Lectura, Lúdica, Orientadora, Repaso, Revisión, Taller, **Observación**, Otras.

## 5. Tipos de tarea y DAG de dependencias

```
A:  a1 (plan anual) → a2 (plan de clases / libro de temas)
B:  a2 → b1 (material didáctico) → b2 (actividad aúlica)
                                  → b3 (síntesis del material)
                                  → b5 (planificación aúlica)
        b2 → b4 (respuestas de la actividad)
C:  b1 (×varios) → c1 (cuestionario) → c2 (respuestas)       [pendiente]
D:  b1 (×varios) → d1 (actividad integradora) → d2 (respuestas) [pendiente]
```

- `a2` es **prerrequisito** de `b1`: contiene la tabla de clases.
- `b1` es **prerrequisito** de `b2`, `b3`, `b5` (usan `{{ material_didactico }}`).
- `b2` es **prerrequisito** de `b4` (usa `{{ actividad_aulica }}`).
- **eje 0 → no genera archivos tipo b** (skip automático: las clases sin dictado no tienen material).
- **Cascada** (pendiente): pedir una tarea principal → genera ella + sus dependientes.

## 6. Tareas tipo B (detalle)

| Código | Tarea | Insumo | Salida |
|---|---|---|---|
| **b1** | Material didáctico | `Tema del Día` + `Actividades` (de `a2`) | Material de estudio ≥20.000 chars |
| **b2** | Actividad aúlica | `{{ material_didactico }}` (b1) | Consigna + roles + tareas (4 integrantes, 1h) |
| **b3** | Síntesis del material | `{{ material_didactico }}` (b1) | Sección "Síntesis y Conclusión" (caracteres, 1 oración, 5 puntos, tiempos) |
| **b4** | Respuestas actividad | `{{ actividad_aulica }}` (b2) | Sección "Resolución de la actividad" |
| **b5** | Planificación aúlica | `{{ material_didactico }}` (b1) | Guía del docente (objetivos, contenidos, secuencia, recursos, evaluación) |

- **Encabezado obligatorio** en todos los tipo b: `Eje (nº + descripción) + Tema del día` al inicio del documento.
- **`b1`** se alimenta de **Tema del día + Actividades** (de `a2`); NO usa Carácter como insumo principal.
- **Sintaxis Feynman + interrogación elaborativa**: van en la capa común (no se repiten en cada tarea).

## 7. Naming de archivos de salida

**Formato:** `<sigla>-<nro_eje><nro_clase_eje>-<Tarea_PascalCase>-<nombre_solo_primera_mayúscula>.md`

- `sigla` (letras, ej. IRI) + `nro_eje` (1 dígito) + `nro_clase_eje` (1 dígito).
- `Tarea` en **PascalCase con `_`**: `Material_Didactico`, `Actividad_Aulica`, `Sintesis`, `Respuestas_Actividad`, `Planificacion_Aulica`, `Plan_Anual`, `Plan_De_Clases`.
- `nombre` = **Primera mayúscula + `_`**, sin tildes, **≤30 caracteres** (truncado a límite de palabra).

Ejemplos:
- `IRI-11-Material_Didactico-Fundamentos_de_redes_de_area.md` (eje 1, clase 1 del eje)
- `IRI-11-Actividad_Aulica-Fundamentos_de_redes_de_area.md` (mismo nombre referencial que b1)
- `IRI-Plan_Anual-Plan_anual.md` (a1, sin código de clase)
- `IRI-Plan_De_Clases-Libro_de_temas.md` (a2)

**Fusión** (pendiente): tareas combinadas unidas con `+`: `<...>-Sintesis+Respuestas_Actividad-<nombre>.md`.

### Nombre referencial compartido

El `Nombre_Referencial` lo **genera el LLM en `b1`** (a partir del título del material). Los archivos `b2`, `b3`, `b4`, `b5` **reutilizan ese mismo nombre** (buscan el archivo `b1` de la clase y extraen su referencial). Así, todos los "b" de una clase comparten nombre.

## 8. Búsqueda de clase

- Por defecto: `--eje N --clase-eje M` (busca `nro_eje=N ∧ nro_clase_eje=M` en `a2`).
- Alternativa: `--id N` (busca la fila con `id=N`; útil para eje 0 donde todas tienen `nro_clase_eje=0`).
- `eje 0` con tarea tipo b → skip automático (mensaje "no se generan archivos tipo b").

## 9. LLM

- Config en `base-comun/config-llm.json` (gitignored; API key del usuario).
- Providers soportados: `llama-cpp` (local, con `disableThinking: true`) y `glm-cloud` (z.ai coding plan).
- Modelo preferido: `glm-4.7` (calidad). glm-4.5-flash descartado (errores).
- Endpoint glm-cloud: `https://api.z.ai/api/coding/paas/v4`.
- `disableThinking` (chat_template_kwargs.enable_thinking=false) sólo para llama.cpp; no aplica a glm-cloud.
- Streaming: el contenido se imprime en vivo.

## 10. Placeholders Jinja2

- Variables de `config-datos.md`: `{{ Variable_Materia }}`, `{{ Carga_Horaria_Anual }}`, `{{ Char_campos }}`, `{{ Cantidad_clases }}`, `{{ Cantidad_ejes }}`, etc.
- Datos de la clase (de `a2`): `{{ eje_numero }}`, `{{ eje_descripcion }}`, `{{ tema }}`, `{{ actividades }}`, `{{ caracter }}`.
- Contenido inyectado: `{{ contenidos_minimos }}` (de `datos-contenidos_minimos.md`).
- Outputs anteriores (encadenamiento): `{{ planificacion_anual }}` (a1), `{{ material_didactico }}` (b1), `{{ actividad_aulica }}` (b2).
- Herencia: las tareas hacen `{% extends "specificacion-principal.md" %}` y rellenan `{% block tarea %}`.

## 11. Output y sobrescritura

- Salida siempre en `output/` (único global).
- Si el archivo existe → la app **pregunta** "¿Sobrescribir? [S/n]", default **Sí**.
- Al final de cada generación se imprime el **tiempo insumido** (`⏱  Xs`).

## 12. Estado de implementación

### ✅ Implementado (v actual)
- `a1`, `a2`, `b1`, `b2`, `b3`, `b4`, `b5` (plantillas Jinja2 + run en main.py).
- Parser de `a2` con 8 columnas canónicas.
- Naming `<sigla>-<nro_eje><nro_clase_eje>-<Tarea>-<nombre≤30>.md`.
- Búsqueda `--eje`/`--clase-eje`/`--id`. Skip eje 0. Tiempo insumido. Sobrescritura con confirmación.
- Nombre referencial compartido b1→b2-b5.
- Encabezado eje+tema en tipo b.

### 🔲 Pendiente (próximas iteraciones)
- **DAG con cascada**: pedir `b1` → genera `b2`,`b3`,`b5` automáticamente (pregunta "¿cascada? S/n").
- **Lote YAML** (`lote/*.yaml`): `interactivo`, `materia`, `tareas`, `clase/clases/eje`, `cascada`, `por_tema`, `fusionar`.
- **Validación de Carácter** desde la app (por ahora sólo en indicaciones de la plantilla).
- **Fusión de documentos** (b3+b4 para imprimir, naming con `+`).
- **Plantillas c1, c2, d1, d2** (evaluación e integradora; el usuario las pasará).
- **Modo `--por-tema`** para b1 (un material por cada `Tema del Día` cuando una clase tenga varios).
- **Actualización del README** a la arquitectura Python (en curso).
