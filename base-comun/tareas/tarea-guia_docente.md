{% extends "specificacion-principal.md" %}

{% block tarea %}
Actuá como docente experto de escuela técnica con amplia experiencia frente a clase. Generá una **Guía Docente** compacta y operativa: una hoja de referencia rápida para conducir la clase, basada en el siguiente material didáctico.

=== MATERIAL DIDÁCTICO ===
{{ material_didactico }}
=== FIN ===

DATOS DE CONTEXTO:
- Curso: {{ Variable_Curso }} | Carrera: {{ Variable_Carrera }} | Materia: {{ Variable_Materia }} | Docente: {{ Variable_Docente }} | Establecimiento: {{ Variable_Establecimiento }}

El documento debe comenzar con el título **GUÍA DOCENTE**, seguido de EXACTAMENTE estas cuatro líneas, CADA UNA EN SU PROPIO RENGLÓN (cada una terminada con DOS ESPACIOS para forzar el salto de línea Markdown):
Materia: {{ Variable_Materia }}  
Docente: {{ Variable_Docente }}  
Eje temático: {{ eje_numero }} — {{ eje_descripcion }}  
Tema: {{ tema }}. {{ actividades }}.

A continuación, desarrollar EXACTAMENTE estas cuatro secciones en este orden:

## 1. Síntesis ultracomprimida
Un único párrafo (no más de 500 caracteres) que responda con densidad: ¿qué tema se cubre?, ¿por qué importa dentro del eje?, ¿qué debe lograr el estudiante al cerrar la clase? Sin listas, sin subtítulos, sin adornos.

## 2. Ejemplos sintéticos
De tres a cinco ejemplos focalizados, listos para garabatear en el pizarrón. Cada ejemplo debe:
- Demostrar UN solo concepto (no mezclar).
- Ser mínimo: no más de 5-6 líneas de desarrollo total por ejemplo.
- ir precedido de una línea que diga qué concepto ilustra.
{% if Incluir_Ejemplos_Codigo == "true" %}
- Cuando el tema involucre programación o sintaxis de consulta (SQL, scripting, etc.), usá código mínimo ejecutable en el lenguaje que corresponda según el tema y los contenidos mínimos (Python, C#, SQL, JavaScript, Bash, etc.). Inferí el lenguaje. Los bloques de código deben ser cortos y comentados brevemente.
{% else %}
- Privilegiá ejemplos conceptuales, analogías concretas o mini-diagramas en texto. No inventar código si la materia no es de programación.
{% endif %}

## 3. Aclaraciones críticas
Notas operativas para el docente, en viñetas, cada una específica al tema (prohibido el consejo genérico aplicable a cualquier clase):
- **Misconceptions**: errores frecuentes o ideas preconcebidas que el estudiante suele traer al aula sobre este tema puntual.
- **Puntos a enfatizar**: conceptos que NO pueden quedar ambiguos durante la explicación.
- **Trampas comunes**: errores típicos al aplicar el concepto (en ejercicios, en la práctica, en examen).
- **Advertencias disciplinarias**: precauciones técnicas, de seguridad o metodológicas particulares del tema (si aplica; si no aplica, omitir esta viñeta).

## 4. Conexiones
Dos a tres renglones en total, sin viñetas:
- Qué tema previo sirve de anclaje para arrancar la explicación.
- Sobre qué tema posterior se apoyará lo visto hoy.

RESTRICCIONES DE TONO Y EXTENSIÓN:
- Lenguaje formal, impersonal, técnico.
- Densidad sobre extensión: cada línea debe aportar información útil al docente frente a la clase. Si una sección se alarga innecesariamente, condensarla.
- Sin introducciones, salutaciones, ni cierres del estilo "espero que esta guía le sea útil".
- Prohibido repetir bloques enteros del material didáctico: la guía condensa, no duplica.
- Documento finalizado.
{% endblock %}
