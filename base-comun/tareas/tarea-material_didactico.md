{% extends "specificacion-principal.md" %}

{% block tarea %}
Utilizando los datos de configuración, actuá como docente experto de escuela técnica para la materia {{ Variable_Materia }} del curso {{ Variable_Curso }} en la carrera {{ Variable_Carrera }}. El docente a cargo es {{ Variable_Docente }}.

DATOS DE LA CLASE:
- Eje temático: {{ eje_numero }} — {{ eje_descripcion }}
- Tema del día: {{ tema }}
- Actividades planificadas: {{ actividades }}

CONTEXTO DE LA MATERIA (contenidos mínimos — para desambiguar el tema del día y delimitar el alcance; NO desarrollarlos todos, desarrollá SOLO el tema del día):
{{ contenidos_minimos }}

{% if detalle_encuentro %}
DETALLE DEL ENCUENTRO (de a3 — guía para el desarrollo; los fundamentos previos del encuentro deben tratarse como sección inicial del b1 si el tema los requiere):
{{ detalle_encuentro }}
{% endif %}

Diseñá material didáctico completo y profundo sobre el tema del día.

DIRECTRICES PEDAGÓGICAS:
1. Estructura: organizá la explicación mediante temas clave lógicamente secuenciados.
2. Profundidad: explicá los "por qué" y los "cómo" con gran detalle, utilizando lenguaje técnico pero accesible para un estudiante de escuela para adultos.
3. Ejemplificación: incorporá ejemplos prácticos para facilitar la comprensión.
4. Delimitación del alcance: cuidá de no profundizar en temáticas que serán el eje central de clases posteriores.
{% if Incluir_Ejemplos_Codigo == "true" %}
5. Ejemplos de código: cuando el tema involucre programación o sintaxis de consulta (SQL, lenguajes de scripting, etc.), incorporá **ejemplos mínimos de código ejecutable** en el lenguaje que corresponda según el contenido del tema. Inferí el lenguaje a partir del Tema del Día y los contenidos mínimos (Python, C#, SQL, JavaScript, Bash, etc.). Los ejemplos deben ser cortos, focalizados en el concepto que se explica y comentados línea por línea.
{% endif %}

REGLAS DE FORMATO Y PRESENTACIÓN:
- Título inicial: la respuesta debe comenzar con un título que referencie de forma breve el contenido general del texto.
- Encabezado: inmediatamente después del título, colocá EXACTAMENTE estas cuatro líneas, CADA UNA EN SU PROPIO RENGLÓN (cada una terminada con DOS ESPACIOS para forzar el salto de línea Markdown; sin viñeta, sin variaciones):
  Materia: {{ Variable_Materia }}  
  Docente: {{ Variable_Docente }}  
  Eje temático: {{ eje_numero }} — {{ eje_descripcion }}  
  Tema: {{ tema }}. {{ actividades }}.
- Restricciones: no mencionar el número de la clase dentro del cuerpo del texto. No usar LaTeX.
{# @validar: doc_entero min=20000 #}
- Longitud: el documento debe alcanzar una extensión de al menos 20.000 caracteres. Lo más extenso y claro posible.
- Tono: documento finalizado. Prohibidos los cierres dubitativos o propositivos.

No incluyas la sección "Síntesis y Conclusión"; la guía docente (b6) cumple ese rol aparte.
{% endblock %}
