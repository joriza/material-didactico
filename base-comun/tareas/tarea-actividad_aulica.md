{% extends "specificacion-principal.md" %}

{% block tarea %}
Actuá como experto en educación de nivel secundario, especializado en técnicas de aprendizaje colaborativo.

El documento debe comenzar con el título, seguido de EXACTAMENTE estas cuatro líneas, CADA UNA EN SU PROPIO RENGLÓN (cada una terminada con DOS ESPACIOS para forzar el salto de línea Markdown):
Materia: {{ Variable_Materia }}  
Docente: {{ Variable_Docente }}  
Eje temático: {{ eje_numero }} — {{ eje_descripcion }}  
Tema: {{ tema }}. {{ actividades }}.

Los equipos de trabajo están conformados por 4 integrantes.

Según el texto del material didáctico entregado a continuación, redactá una actividad que indique claramente que debe realizarse llevando a cabo una técnica de aprendizaje colaborativo, pero sin indicar cuál es la técnica utilizada en la consigna de la actividad.

=== MATERIAL DIDÁCTICO DE REFERENCIA ===
{{ material_didactico }}
=== FIN DEL MATERIAL ===

Tener en cuenta que los escenarios son simulados, porque la escuela no cuenta con hardware de red suficiente para realizar una práctica real.

Detallar claramente las siguientes secciones:
- Consigna de Trabajo
- Roles de cada integrante del Equipo
- Tareas a Realizar

La actividad debe poder ser realizada por los alumnos en un término de 1h.

REGLA IMPORTANTE: cada integrante del equipo debe conservar una copia manuscrita de cada resolución para formar parte de la carpeta técnica como uno de los puntos para acreditar la materia a fin de ciclo.
{% endblock %}
