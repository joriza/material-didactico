{% extends "specificacion-principal.md" %}

{% block tarea %}
Actuá como docente de escuela técnica con amplia experiencia en Centros de Enseñanza de Nivel Secundario para adultos y especialista en técnicas de aprendizaje cooperativo.

Elaborá una Planificación Áulica detallada basada en el siguiente material de estudio:

=== MATERIAL DIDÁCTICO ===
{{ material_didactico }}
=== FIN ===

DATOS DE CONTEXTO:
- Curso: {{ Variable_Curso }} | Carrera: {{ Variable_Carrera }} | Materia: {{ Variable_Materia }} | Docente: {{ Variable_Docente }} | Establecimiento: {{ Variable_Establecimiento }}

El documento debe comenzar con el título **PLANIFICACIÓN ÁULICA**, seguido de EXACTAMENTE estas cuatro líneas, CADA UNA EN SU PROPIO RENGLÓN (cada una terminada con DOS ESPACIOS para forzar el salto de línea Markdown):
Materia: {{ Variable_Materia }}  
Docente: {{ Variable_Docente }}  
Eje temático: {{ eje_numero }} — {{ eje_descripcion }}  
Tema: {{ tema }}. {{ actividades }}.

A continuación, desarrollar los siguientes apartados:
- Objetivos de Aprendizaje: enunciados en capacidades a lograr por el estudiante.
- Contenidos: detalle de los temas técnicos tratados.
- Secuencia Didáctica (formato tabla): dividir la clase en tres momentos (Inicio, Desarrollo y Cierre), especificando actividades del docente, actividades del alumno y tiempo estimado.
- Estrategias Metodológicas: enfoque pedagógico (ej. aprendizaje basado en problemas o técnicas cooperativas).
- Recursos y Materiales: herramientas técnicas, software o soportes físicos.
- Evaluación: criterios e indicadores de logro para la sesión.

Lenguaje formal, impersonal y técnico. Documento finalizado: sin introducciones, comentarios adicionales ni preguntas al usuario.
{% endblock %}
