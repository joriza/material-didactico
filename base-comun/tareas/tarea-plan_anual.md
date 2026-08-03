{% extends "specificacion-principal.md" %}

{% block tarea %}
Actuá como docente de escuela secundaria de la Provincia de Buenos Aires. Tu objetivo es diseñar una planificación anual detallada.

DATOS DE CONTEXTO:
- Materia: {{ Variable_Materia }} | Curso: {{ Variable_Curso }} | Carrera: {{ Variable_Carrera }} | Docente: {{ Variable_Docente }}
- Carga horaria anual: {{ Carga_Horaria_Anual }} | Frecuencia: {{ Frecuencia }} | Carga por encuentro: {{ Carga_Horaria_encuentro }}
- Cantidad total de ejes temáticos: {{ Cantidad_ejes }}

La planificación debe ajustarse estrictamente a los siguientes contenidos mínimos:
{{ contenidos_minimos }}

Comenzar mostrando datos identificatorios.

#### 1. REGLAS DE ORGANIZACIÓN TEMPORAL

La estructura de la tabla de planificación debe seguir este orden cronológico estricto.

REGLAS DE CALENDARIO (para todo el ciclo lectivo):
{{ Reglas_ciclo_lectivo }}

- Consta de 2 cuatrimestres de 18 clases cada uno (36 clases anuales totales).

REGLAS POR CUATRIMESTRE (estructura fija):
{{ Reglas_cuatrimestres }}

Cada cuatrimestre, en este orden cronológico estricto:

1. **Intensificación inicial (2 clases)** para profundización de saberes.
   - En el **1° cuatrimestre**: la PRIMERA intensificación incluye además Presentación, Diagnóstico y Acuerdo Pedagógico (si es escuela técnica, sumar Seguridad y elementos de protección personal referidos al entorno en actividades prácticas). Trabaja saberes previos del año anterior.
   - En el **2° cuatrimestre**: ambas intensificaciones iniciales trabajan saberes previos (los dictados en el 1° cuatrimestre).

2. **Eje temático 1 del cuatrimestre (6 clases)**: 5 clases de desarrollo de contenido + 1 clase de Evaluación escrita al final. No colocar la palabra "eje" en el nombre del eje temático.

3. **Eje temático 2 del cuatrimestre (7 clases)**: 5 clases de desarrollo de contenido + 1 clase de Repaso y Consultas + 1 clase de Evaluación escrita al final. No colocar la palabra "eje" en el nombre del eje temático.

4. **Intensificación final (2 clases)** para trabajar saberes no alcanzados durante el cuatrimestre.

5. **Cierre + volcado de notas (1 clase)**.
   - En el **1° cuatrimestre**: cierre del cuatrimestre + volcado de notas parciales.
   - En el **2° cuatrimestre**: cierre anual + volcado a libreta de calificaciones. Es la **última clase del año regular** para los alumnos que no requieren intensificación. Las intensificaciones posteriores (diciembre/marzo) son para los que deben recuperar saberes no acreditados.

DISTRIBUCIÓN TOTAL ANUAL (constante, no negociable):
- 8 intensificaciones (4 iniciales + 4 finales).
- 4 ejes temáticos × (5 contenido + 1 evaluación escrita) = 24 clases.
- 2 clases de Repaso y Consultas (en los segundos ejes de cada cuatrimestre).
- 2 cierres (uno por cuatrimestre).
- **Total: 8 + 24 + 2 + 2 = 36 clases.**

#### 2. METODOLOGÍA Y FORMATO DE TABLA

- **Carga Horaria**: Distribuir los contenidos según `{{ Carga_Horaria_Anual }}`, con `{{ Frecuencia }}` y `{{ Carga_Horaria_encuentro }}`.
- **Columna de Tiempo**: colocar exclusivamente la **cantidad de clases**. Está prohibido colocar rangos numéricos (ej. "1 a 4").
- **Metodología**: emplear técnicas de Aprendizaje Colaborativo con actividades diseñadas para realizarse íntegramente en clase.
- **Columnas Obligatorias**: Cuatrimestre, EJE TEMÁTICO (con denominación), TIEMPO (cantidad de clases), CONTENIDOS, Expectativas de Logro, ACTIVIDADES (especificar uso de celular), TP OBLIGATORIO, TÉCNICAS/CAPACIDADES, RECURSOS, METODOLOGÍA DE EVALUACIÓN.
- En la cantidad de clases solo colocar el número.

#### 3. SECCIÓN DE INTENSIFICACIÓN

De forma separada, detallá 6 instancias de intensificación en formato tabla (las 4 primeras guardan relación con las intensificaciones de la planificación anual, las 2 últimas son integradoras de la materia):
- Cada instancia será en los meses estipulados por la normativa vigente.
- CONTENIDOS MÍNIMOS IRRENUNCIABLES.
- ACTIVIDAD Y/O METODOLOGÍA ACORDADA (Ultra-Condensada).
- RECURSOS ACORDADOS (Condensado al 25%).
- (Las instancias 5 y 6 corresponden a Diciembre y Marzo para estudiantes que no acreditaron saberes previos).

#### 4. OBSERVACIONES DE CALENDARIO

#### 5. Sección Resumen

De forma separada, presentar:
- Expectativas de logros generales.
- Evaluación de capacidades (nombre del proyecto y materias o entornos formativos involucrados).
- PROYECTOS ÁULICOS / INSTITUCIONALES / SALIDAS EDUCATIVAS (nombre del proyecto, breve descripción, fecha, materias o entornos formativos involucrados).
- Observaciones (indicar que, bajo conocimiento de saberes previos, la planificación es flexible y podrá ajustarse según el ritmo de aprendizaje del grupo y la disponibilidad de materiales específicos).

El registro de las clases de consolidación y evaluación dependerá de `{{ Tipo_de_Clase }}`. Si se indica 'Taller', se unificarán en una sola fila con tiempo 2; en caso contrario, se desglosarán en dos filas con tiempo 1 cada una.

REGLA DE ORO:
- Expresá en una única tabla la planificación.
- Las clases de consolidación y evaluación deben expresarse en una única fila denominada 'Consolidación y Evaluación'. En la columna TIEMPO se debe consignar el número 2, evitando cualquier desglose individual de dichas clases.
- Desarrollá un poco más el texto de las celdas de las columnas de Contenidos y Actividad.
{% endblock %}
