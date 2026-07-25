{% extends "specificacion-principal.md" %}

{% block tarea %}
Diseñá material de estudio completo y profundo.

DATOS DE CONTEXTO:
- Materia: {{ Variable_Materia }}
- Carrera: {{ Variable_Carrera }}
- Curso: {{ Variable_Curso }}
- Docente a cargo: {{ Variable_Docente }}

Organizá la explicación por temas clave, con ejemplos para mejorar la comprensión. Explicá los "por qué" y los "cómo" con gran detalle, utilizando lenguaje técnico pero accesible para un estudiante de escuela para adultos.

MARCO DE REFERENCIA:
- Carácter de la clase: {{ caracter }}  (orienta el enfoque del material)
{% if eje_tematico %}- Eje temático: {{ eje_tematico }}{% endif %}

TEMAS A DESARROLLAR EN ESTA CLASE:
{% for tema in temas %}
- {{ tema }}
{% endfor %}

REGLAS DE PRESENTACIÓN:
- Como título del documento, colocá una versión sintética de los temas tratados.
- Indicá el número y nombre del eje temático.
- Detallá todos los temas a tratar en esta clase. Si es una clase de repaso (carácter "Repaso"), debe indicarlo explícitamente.

LONGITUD: el documento debe tener **al menos 20000 caracteres** (incluyendo espacios).

No incluyas el número de clase en el texto del documento.

No escribas la sección "Síntesis y Conclusión"; esa sección se genera como tarea aparte.
{% endblock %}
