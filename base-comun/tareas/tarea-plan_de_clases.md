{% extends "specificacion-principal.md" %}

{% block tarea %}
Generá el contenido para un libro de temas detallado de la materia.

DATOS DE CONTEXTO:
- Materia: {{ Variable_Materia }} | Curso: {{ Variable_Curso }} | Carrera: {{ Variable_Carrera }} | Docente: {{ Variable_Docente }}
- Carga horaria anual: {{ Carga_Horaria_Anual }} | Encuentros: {{ Frecuencia }} de {{ Carga_Horaria_encuentro }}
- Tipo de detalle: {{ Tipo_Detalle }}
- Total de encuentros: {{ Cantidad_clases }} (salvo que se indique lo contrario)

Los ejes temáticos y su duración se encuentran en la siguiente planificación anual:
{{ planificacion_anual }}

Metodología: todas las actividades deben emplear técnicas de Aprendizaje Colaborativo, con duración suficiente para ser realizadas íntegramente en clase.

Actuá como asistente pedagógico especializado en gestión documental escolar.

REGLAS DE PRESENTACIÓN:
- La información debe estar organizada estrictamente en una tabla con las siguientes columnas:
  - Nº Clase: secuencia numérica correspondiente.
  - Eje Temático: nombre del Eje temático.
  - Nº Eje: identificador del eje temático.
  - Carácter/Objetivo: selección obligatoria del listado adjunto.
  - Tema del Día: descripción sintética del contenido.
  - Actividades: detalle de las acciones pedagógicas a desarrollar.
  - Fecha: (no estimar; la colocará el docente manualmente).

RESTRICCIONES TÉCNICAS:
- Longitud: ningún campo debe exceder los {{ Char_campos }} caracteres.
- Vocabulario Controlado (columna "Carácter/Objetivo"), sólo se permite:
  Presentación, Diagnóstico, Teórica, Práctica, Teórico-Práctica, Dialogada, Reflexiva, Aplicación, Argumentativa, Evaluativa, Evaluativa (en proceso o final), Experimental, Fijación, Informativa, Integración, Interpretativa, Investigación, Lectura, Lúdica, Orientadora, Repaso, Revisión, Taller, Observación, Otras.

Procedimiento: confirmá la lectura de las variables y procedé con el desarrollo pedagógico basado en los siguientes contenidos mínimos:
{{ contenidos_minimos }}
{% endblock %}
