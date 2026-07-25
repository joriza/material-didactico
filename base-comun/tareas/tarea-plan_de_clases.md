{% extends "specificacion-principal.md" %}

{% block tarea %}
Generá el contenido para un libro de temas detallado de la materia.

DATOS DE CONTEXTO:
- Materia: {{ Variable_Materia }} | Curso: {{ Variable_Curso }} | Carrera: {{ Variable_Carrera }} | Docente: {{ Variable_Docente }}
- Carga horaria anual: {{ Carga_Horaria_Anual }} | Encuentros: {{ Frecuencia }} de {{ Carga_Horaria_encuentro }}
- Total de encuentros: {{ Cantidad_clases }} | Cantidad de ejes con dictado: {{ Cantidad_ejes }}

Los ejes temáticos y su duración se encuentran en la siguiente planificación anual:
{{ planificacion_anual }}

Metodología: todas las actividades deben emplear técnicas de Aprendizaje Colaborativo, con duración suficiente para realizarse íntegramente en clase.

Actuá como asistente pedagógico especializado en gestión documental escolar.

REGLAS DE PRESENTACIÓN:
- La información debe estar organizada estrictamente en una tabla con las siguientes columnas, EN ESTE ORDEN EXACTO:
  1. **id**: número secuencial global, comenzando en 1 (debe llegar hasta {{ Cantidad_clases }}).
  2. **Eje**: nombre/descripción del Eje temático.
  3. **nro_eje**: número del eje. Valor `0` para clases que NO son de dictado de contenido (presentación, diagnóstico, cierre, evaluación, intensificación); valores `1` a `{{ Cantidad_ejes }}` para los ejes con dictado.
  4. **nro_clase_eje**: número secuencial de la clase DENTRO del eje. **Si nro_eje=0, entonces nro_clase_eje=0 siempre.**
  5. **Carácter/Objetivo**: selección obligatoria del listado adjunto.
  6. **Tema del Día**: descripción sintética del contenido.
  7. **Actividades**: detalle de las acciones pedagógicas a desarrollar.
  8. **Fecha**: (no estimar; la colocará el docente manualmente).

RESTRICCIONES TÉCNICAS:
- Ningún campo debe exceder los {{ Char_campos }} caracteres.
- Vocabulario controlado (columna "Carácter/Objetivo"), sólo se permite:
  Presentación, Diagnóstico, Teórica, Práctica, Teórico-Práctica, Dialogada, Reflexiva, Aplicación, Argumentativa, Evaluativa, Evaluativa (en proceso o final), Experimental, Fijación, Informativa, Integración, Interpretativa, Investigación, Lectura, Lúdica, Orientadora, Repaso, Revisión, Taller, Observación, Otras.

Procedimiento: confirmá la lectura de las variables y procedé con el desarrollo pedagógico basado en los siguientes contenidos mínimos:
{{ contenidos_minimos }}
{% endblock %}
