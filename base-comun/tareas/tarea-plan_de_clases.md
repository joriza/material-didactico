{% extends "specificacion-principal.md" %}

{% block tarea %}
Generá el contenido para un libro de temas detallado de la materia.

DATOS DE CONTEXTO:
- Materia: {{ Variable_Materia }} | Curso: {{ Variable_Curso }} | Carrera: {{ Variable_Carrera }} | Docente: {{ Variable_Docente }}
- Carga horaria anual: {{ Carga_Horaria_Anual }} | Encuentros: {{ Frecuencia }} de {{ Carga_Horaria_encuentro }}
- Total de encuentros: {{ Cantidad_clases }} | Cantidad de ejes con dictado: {{ Cantidad_ejes }}
- Temas por encuentro (default orientativo, NO determinista): {{ Temas_por_encuentro | default(1) }}

Los ejes temáticos y su duración se encuentran en la siguiente planificación anual:
{{ planificacion_anual }}

Metodología: todas las actividades deben emplear técnicas de Aprendizaje Colaborativo, con duración suficiente para realizarse íntegramente en clase.

Actuá como asistente pedagógico especializado en gestión documental escolar.

REGLAS DE PRESENTACIÓN:
- La información debe estar organizada estrictamente en una tabla con las siguientes columnas, EN ESTE ORDEN EXACTO:
  1. **id**: número secuencial global, comenzando en 1 (debe llegar hasta {{ Cantidad_clases }}). **Identifica ENCUENTRO, no fila**: si un encuentro tiene varios temas, todas sus filas comparten el mismo `id`.
  2. **Eje**: nombre/descripción del Eje temático.
  3. **nro_eje**: número del eje. Valor `0` para clases que NO son de dictado de contenido (presentación, diagnóstico, cierre, evaluación, intensificación); valores `1` a `{{ Cantidad_ejes }}` para los ejes con dictado. Un solo dígito (máximo 9).
  4. **nro_clase_eje**: número secuencial de la clase DENTRO del eje. **Si nro_eje=0, entonces nro_clase_eje=0 siempre.** Un solo dígito (máximo 9).
  5. **Tema_Nro**: número del tema DENTRO del encuentro. Valor `1` si el encuentro trata un solo tema; `1`, `2`, (excepcionalmente `3`) si el encuentro trata varios temas. Un solo dígito (máximo 9).
  6. **Carácter/Objetivo**: selección obligatoria del listado adjunto.
  7. **Tema del Día**: descripción sintética del contenido del tema (uno distinto por fila cuando haya varios temas en el mismo encuentro).
  8. **Actividades**: detalle de las acciones pedagógicas a desarrollar.
  9. **Fecha**: (no estimar; la colocará el docente manualmente).

REGLAS DE ESTRUCTURA POR CUATRIMESTRE (constante, no negociable):
- 2 cuatrimestres × 18 clases = 36 clases anuales.
- Cada cuatrimestre sigue este orden cronológico estricto:
  1. **Intensificación inicial (2 clases)** con `nro_eje=0`, `nro_clase_eje=0`. `Carácter`: *Presentación* en la primera del 1° cuatrimestre (incluye diagnóstico), *Intensificación* en las demás.
  2. **Eje 1 del cuatrimestre**: 5 clases de contenido (`nro_eje=1` o `nro_eje=3` según cuatrimestre) con `Carácter` según el tema (*Teórica*, *Práctica*, *Teórico-Práctica*, etc.) + 1 clase final con `Carácter`: *Evaluativa*.
  3. **Eje 2 del cuatrimestre**: 5 clases de contenido (`nro_eje=2` o `nro_eje=4`) + 1 clase con `Carácter`: *Repaso* + 1 clase final con `Carácter`: *Evaluativa*.
  4. **Intensificación final (2 clases)** con `nro_eje=0`, `Carácter`: *Intensificación*.
  5. **Cierre + volcado de notas (1 clase)** con `nro_eje=0`, `Carácter`: *Cierre* (o *Evaluativa (en proceso o final)*). En el 2° cuatrimestre es cierre anual + volcado a libreta (última clase del año regular).

REGLAS DE MULTI-TEMA POR ENCUENTRO:
- `{{ Temas_por_encuentro | default(1) }}` es un valor ORIENTATIVO por defecto. La decisión final sobre cuántos temas tiene cada encuentro la tomás vos según la dinámica prevista de la clase: un encuentro puede tener 1 tema y otro del mismo eje tener 2, ambos son válidos.
- Para cada `(nro_eje, nro_clase_eje)` con dictado, emitís UNA fila por tema. Todas las filas del mismo encuentro comparten `id`, `nro_eje` y `nro_clase_eje`. Solo varían `Tema_Nro` (1, 2, …) y `Tema del Día` (uno distinto por fila). El resto de los campos (`Carácter`, `Actividades`, `Fecha`) pueden repetir o variar según corresponda pedagógicamente.
- Para encuentros de un solo tema: una única fila con `Tema_Nro = 1`.

RESTRICCIONES TÉCNICAS:
- Ningún campo debe exceder los {{ Char_campos }} caracteres.
- Cada componente numérico del identificador (`nro_eje`, `nro_clase_eje`, `Tema_Nro`) es un solo dígito (1-9). Si alguna materia superara 9 ejes, 9 clases por eje o 9 temas por encuentro, esto rompe el naming; avisalo en lugar de inventar.
- Vocabulario controlado (columna "Carácter/Objetivo"), sólo se permite:
  Presentación, Diagnóstico, Teórica, Práctica, Teórico-Práctica, Dialogada, Reflexiva, Aplicación, Argumentativa, Evaluativa, Evaluativa (en proceso o final), Experimental, Fijación, Informativa, Integración, Interpretativa, Investigación, Lectura, Lúdica, Orientadora, Repaso, Revisión, Taller, Observación, Otras.

Procedimiento: confirmá la lectura de las variables y procedé con el desarrollo pedagógico basado en los siguientes contenidos mínimos:
{{ contenidos_minimos }}
{% endblock %}
