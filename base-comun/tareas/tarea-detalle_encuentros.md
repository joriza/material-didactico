{% extends "specificacion-principal.md" %}

{% block tarea %}
Actuá como docente experto de educación técnica. Generá el **detalle completo de cada encuentro** del año lectivo, como insumo para generar el material didáctico (b1) y derivados.

DATOS DE CONTEXTO:
- Materia: {{ Variable_Materia }} | Curso: {{ Variable_Curso }} | Carrera: {{ Variable_Carrera }} | Docente: {{ Variable_Docente }}
- Carga horaria anual: {{ Carga_Horaria_Anual }} | Encuentros: {{ Frecuencia }} de {{ Carga_Horaria_encuentro }}
- Total de encuentros: {{ Cantidad_clases }} | Cantidad de ejes con dictado: {{ Cantidad_ejes }}

La planificación anual de referencia:
{{ planificacion_anual }}

El libro de temas (a2) de referencia:
{{ plan_de_clases }}

Los contenidos mínimos de la materia:
{{ contenidos_minimos }}

REGLA DE PROGRESIÓN PEDAGÓGICA:
Aplicá la regla del plan anual (saberes previos asumedos vs fundamentos previos propios del lenguaje/tecnología a desarrollar). Desarrollá los fundamentos previos explícitamente en el encuentro que los necesita, no solo como mención.

FORMATO DE SALIDA — por cada encuentro del libro de temas (a2):

## Encuentro id=N (nro_eje=N, nro_clase_eje=N)

[Si el encuentro tiene varios temas (multi-tema), repetir el bloque siguiente por cada Tema_Nro.]

### Tema M: {Tema del Día}

**Carácter/Objetivo:** {Carácter}

**Tema desarrollado:**
[Párrafos extensos desarrollando el tema del día. Sin restricciones de longitud. Profundizá causas, efectos, mecanismos y ejemplos.]

**Fundamentos previos:**
[Lista de conceptos prerrequisito con desarrollo completo de cada uno. Si el concepto es "saber previo" (de años anteriores), solo una mención breve. Si es "fundamento previo propio del lenguaje/tecnología" (mutabilidad, decoradores, inyección de dependencias, DOM, etc.), desarrollo sustancial.]

**Objetivos específicos del encuentro:**
[Lista de objetivos operativos que el alumno debe lograr.]

**Prerrequisitos asumidos:**
[Saberes que se asume que el alumno ya domina. No desarrollar.]

REGLAS DE PRESENTACIÓN:
- Una sección `## Encuentro` por cada fila del libro de temas (a2).
- Si un encuentro tiene varios temas (multi-tema), cada tema con su sub-sección `### Tema M:`.
- Identificación SIEMPRE por `id` global + `nro_eje` + `nro_clase_eje` + `tema_nro`.
- Sin restricciones de longitud por campo (diferencia clave con a2, que respeta `Char_campos`).
- Para encuentros de Carácter "Intensificación" o "Cierre", desarrollá contenido apropiado al tipo.
- Para encuentros de Carácter "Evaluativa", dejá registro de qué contenidos evalúa y qué se espera que el alumno demuestre.

RESTRICCIÓN: respetá EXACTAMENTE los identificadores del a2 (id, nro_eje, nro_clase_eje, tema_nro). No inventes encuentros nuevos ni omitas ninguno.
{% endblock %}
