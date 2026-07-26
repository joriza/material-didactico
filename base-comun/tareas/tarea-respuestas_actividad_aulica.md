{% extends "specificacion-principal.md" %}

{% block tarea %}
El documento debe comenzar con el título, seguido de EXACTAMENTE estas cuatro líneas, CADA UNA EN SU PROPIO RENGLÓN (cada una terminada con DOS ESPACIOS para forzar el salto de línea Markdown):
Materia: {{ Variable_Materia }}  
Docente: {{ Variable_Docente }}  
Eje temático: {{ eje_numero }} — {{ eje_descripcion }}  
Tema: {{ tema }}. {{ actividades }}.

Generá la sección "Resolución de la actividad" para la siguiente actividad áulica:

=== ACTIVIDAD ÁULICA ===
{{ actividad_aulica }}
=== FIN ===

Sección 2 (Título: "Resolución de la actividad"): explicación técnica de la metodología colaborativa elegida y el solucionario esperado. Fundamentá el "cómo" y el "por qué" de las respuestas propuestas.
{% endblock %}
