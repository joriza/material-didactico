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

La estructura de la tabla de planificación debe seguir este orden cronológico.

REGLAS DE CALENDARIO (para todo el ciclo lectivo):
{{ Reglas_ciclo_lectivo }}

- Consta de 2 cuatrimestres de 18 clases cada uno.

REGLAS POR CUATRIMESTRE:
{{ Reglas_cuatrimestres }}

- Presentación, diagnóstico y acuerdo pedagógico: 1 clase. Solo para el primer cuatrimestre. Solo si es escuela técnica, agregar en la misma clase Seguridad y elementos de protección personal referidos al entorno en actividades prácticas de la materia.
- Intensificación: 2 clases. Ubicadas al inicio de cada cuatrimestre para profundización de saberes.
- Desarrollo del Eje temático: 4 clases. No colocar la palabra "eje" en el nombre del eje temático.
- Consolidación, repaso y consulta de dudas técnicas + Evaluación: 2 clases. Si en `{{ Tipo_de_Clase }}` se indica 'Taller', se unificarán en una sola fila con tiempo 2; en caso contrario, se desglosarán en dos filas con tiempo 1 cada una.
- Desarrollo del Eje temático: 4 clases. No colocar la palabra "eje" en el nombre del eje temático.
- Consolidación, repaso y consulta de dudas técnicas + Evaluación: 2 clases. (Misma regla anterior según `{{ Tipo_de_Clase }}`.)
- Cierre del cuatrimestre: 1 clase.
- Cierre de la materia: 1 clase. Solo para el segundo cuatrimestre.
- Intensificación: 2 clases. Ubicadas al final de cada cuatrimestre para profundización de saberes.

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
