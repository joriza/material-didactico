{% extends "specificacion-principal.md" %}

{% block tarea %}
El documento debe comenzar con el título, seguido de EXACTAMENTE estas cuatro líneas, CADA UNA EN SU PROPIO RENGLÓN (cada una terminada con DOS ESPACIOS para forzar el salto de línea Markdown):
Materia: {{ Variable_Materia }}  
Docente: {{ Variable_Docente }}  
Eje temático: {{ eje_numero }} — {{ eje_descripcion }}  
Tema: {{ tema }}. {{ actividades }}.

Generá la sección "Síntesis y Conclusión" para el siguiente material didáctico:

=== MATERIAL DIDÁCTICO ===
{{ material_didactico }}
=== FIN DEL MATERIAL ===

La sección debe ir bajo el título exacto "Síntesis y Conclusión" y contener únicamente estos cuatro puntos:
* Cantidad exacta de caracteres del material.
* Una síntesis global del tema de exactamente una oración.
* Una síntesis muy corta de los 5 puntos más importantes.
* Tiempo estimado de lectura (con toma de apuntes y sin toma de apuntes).
{% endblock %}
