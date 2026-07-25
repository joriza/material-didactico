# Diseño del sistema — z-material-didactico

Documento de arquitectura. Fuente única de las decisiones de diseño. Las reglas pedagógicas/formato viven en `base-comun/specificacion-principal.md`; este archivo describe la **arquitectura** de la app.

---

## 1. Stack

- **Python ≥ 3.10** + **Jinja2** (plantillas con herencia) + **PyYAML** (lotes y manifiesto) + lib **`openai`** (streaming, OpenAI-compatible).
- Un solo entrypoint: `main.py`. Sin frameworks.

## 2. Capas (3 niveles de variación)

| Capa | Variación | Dónde |
|---|---|---|
| **Común** | No varía | `base-comun/specificacion-principal.md`, `base-comun/config-llm.json`, `base-comun/tareas/`, `base-comun/tareas.yaml` |
| **Tareas** (la "variante superior") | Por tipo de tarea; **iguales para toda materia** | `base-comun/tareas/tarea-*.md` (plantillas Jinja2) |
| **Datos auxiliares** | Por materia; intercambiables | `materias/<sigla>/*.md` (sueltos) |

Las tareas **heredan** la capa común (Jinja2 `{% extends %}`). Los datos rellenan los placeholders.

## 3. Estructura de carpetas

```
z-material-didactico/
├── base-comun/
│   ├── specificacion-principal.md      ← capa común (base Jinja2)
│   ├── config-llm.json                 ← LLM común (llama-cpp / glm-cloud)
│   ├── tareas.yaml                     ← manifiesto (jerarquía + dependencias)
│   └── tareas/                         ← plantillas de tarea (comunes)
│       ├── tarea-plan_anual.md
│       ├── tarea-plan_de_clases.md
│       ├── tarea-material_didactico.md
│       ├── tarea-actividad_aulica.md
│       └── ...
├── materias/
│   └── IRI/                            ← Redes (datos sueltos)
│       ├── config-datos.md
│       ├── datos-contenidos_minimos.md
│       └── ejemplo-planificacion_de_clases.md
├── lote/                               ← lotes YAML (comunes a todas las materias)
├── output/                             ← output único global (naming ordena)
├── design.md                           ← este documento
├── main.py                             ← app
└── requirements.txt
```

## 4. Tipos de tarea y DAG de dependencias

```
A:  a1 (plan anual) → a2 (plan de clases / libro de temas)
B:  a2 → b1 (material didáctico) → b2 (actividad aúlica)
                                  → b3 (síntesis del material)
                                  → b5 (planificación aúlica)
        b2 → b4 (respuestas de la actividad)
C:  b1 (×varios, por naming) → c1 (cuestionario) → c2 (respuestas)
D:  b1 (×varios, por naming) → d1 (actividad integradora) → d2 (respuestas)
```

- `a2` es **prerrequisito obligatorio** de `b1/c1/d1`: contiene la tabla de clases.
- **Cascada:** pedir una tarea principal → genera ella + sus dependientes (definidos en `tareas.yaml`).
- El lote puede pedir subconjuntos (ej. `b2+b4`).
- **Modo interactivo:** si la tarea tiene subordinados → pregunta "¿cascada? (S/n)" default Sí. En lote `interactivo: false` → aplica defaults sin preguntar.

## 5. Tabla `a2` (7 columnas, insumo canónico de clases)

| Clase | Eje | Eje Temático | Carácter/Objetivo | Tema del Día | Actividades | Fecha |
|---|---|---|---|---|---|---|

- Cada clase puede tener N filas (N temas); el **Nº de tema es implícito** (orden de la fila dentro de la misma Clase).
- **`Tema del Día`** = contenido que `b1` desarrolla (el que manda).
- **`Carácter/Objetivo`** = orienta el enfoque del material (Teórica/Práctica/Repaso…); la app **valida** contra el vocabulario controlado.
- `Char_campos = 35` (límite oficial por campo).

**Vocabulario controlado de Carácter/Objetivo:**
Presentación, Diagnóstico, Teórica, Práctica, Teórico-Práctica, Dialogada, Reflexiva, Aplicación, Argumentativa, Evaluativa, Evaluativa (en proceso o final), Experimental, Fijación, Informativa, Integración, Interpretativa, Investigación, Lectura, Lúdica, Orientadora, Repaso, Revisión, Taller, **Observación**, Otras.

## 6. `b1` (material didáctico)

- **Default:** un material **por clase** (temas combinados con `{% for tema in temas %}`).
- `por_tema: true` en el lote → un material por tema (itera la plantilla por cada `Tema del Día`).
- Genera el `Nombre_Referencial` (lo produce el LLM); los derivados (`b2`,`b3`,`b4`,`b5`) y la fusión **reutilizan** ese mismo nombre.

## 7. Naming

`<sigla>-<eje><sec>[<tema>]-<Tarea_PascalCase>-<nombre_solo_primera_mayúscula>.md`

- `sigla` (letras) + `eje` (1 dígito) + `sec` (1 dígito) + `tema` (1 dígito, sólo si `por_tema`).
- `Tarea` en **PascalCase con `_`**: `Material_Didactico`, `Actividad_Aulica`, `Sintesis`, `Respuestas_Actividad`, `Planificacion_Aulica`, `Cuestionario_Evaluacion`, `Actividad_Integradora`, `Plan_Anual`, `Plan_De_Clases`.
- `nombre` = Primera mayúscula + `_`, sin tildes.
- **Fusión:** tareas combinadas unidas con `+`: `<...>-Sintesis+Respuestas_Actividad-<nombre>.md`.

Ej.: `IRI-231-Material_Didactico-Configuracion_y_asignacion_de_direcciones_ip.md`

## 8. Manifiesto `base-comun/tareas.yaml`

Define, por código de tarea: archivo plantilla, dependencias (`depende_de`), subordinados (`dependientes`), iteración (`por_clase`/`por_tema`), multi-insumo (`c1`/`d1`), y **grupos de fusión**.

## 9. Lote (`lote/*.yaml`)

```yaml
interactivo: false          # OBLIGATORIO al inicio del archivo
materia: IRI
tareas: [b1]                # o subconjunto [b2, b4]
clase: "23"                 # una clase  | clases: ["23","24"]  | eje: 2 (todas)
cascada: true               # default; se omite la pregunta si no-interactivo
por_tema: false             # default: combinado por clase
fusionar: impresion_docente # opcional (grupo definido en tareas.yaml)
```

## 10. Output y sobrescritura

- Salida siempre en `output/` (único global).
- Si el archivo ya existe → la app **pregunta**, default = **sobrescribir**.

## 11. Especificación de placeholders (Jinja2)

- Variables de `config-datos.md`: `{{ Variable_Materia }}`, `{{ Carga_Horaria_Anual }}`, `{{ Char_campos }}`, etc.
- Contenido inyectado: `{{ contenidos_minimos }}` (de `datos-contenidos_minimos.md`).
- Outputs anteriores (encadenamiento): `{{ planificacion_anual }}` (output de `a1`), `{{ material_didactico }}` (output de `b1`).
- Herencia: las tareas hacen `{% extends "specificacion-principal.md" %}`.
