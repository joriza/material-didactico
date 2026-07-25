# ## 1-Material Didactico Prompt V2.1

# [VARIABLES DE CONFIGURACIÓN]
> Instrucción para el usuario humano: Complete o modifique los valores entre comillas antes de ejecutar el prompt.

[ARCHIVO_CONFIG]: "01-variables_configuracion.md"
[ARCHIVO_PLANIFICACION]: "21-draft-planificacion.md"
[ARCHIVO_CLASES]: "22-draft-planificacion_de_clases.md"

[MATERIA]: "Ingresar Materia"
[CURSO]: "Ingresar Curso"
[CARRERA]: "Ingresar Carrera"
[DOCENTE]: "Ingresar Nombre del Docente"

# [TEMA DEL DÍA - ZONA DE EDICIÓN FRECUENTE]
> Instrucción para el usuario humano: Modifique estos parámetros para cada nueva clase. Si se deja [TEMA_A_TRATAR] en blanco, el sistema tomará automáticamente el tema del archivo de planificación de clases.

[NUMERO_CLASE]: "11"
[TEMA_A_TRATAR]: "Temporizadores en el PLC. Programación de retardos" 

---

# [ROL Y CONTEXTO]
Utilizando los datos extraídos de los documentos indicados en [ARCHIVO_CONFIG] y [ARCHIVO_CLASES], actúe como docente experto de escuela técnica para la materia [MATERIA] del curso [CURSO] en la carrera [CARRERA]. El docente a cargo es [DOCENTE].

Como marco de referencia, se debe tomar el eje temático correspondiente a la clase [NUMERO_CLASE] establecido en el documento [ARCHIVO_PLANIFICACION].

# [DETERMINACIÓN DEL TEMA Y TAREA PRINCIPAL]
Se requiere diseñar material didáctico completo y profundo.
Para determinar los temas a tratar, se debe aplicar la siguiente lógica condicional:
- Si la variable [TEMA_A_TRATAR] está vacía o en blanco, se deben extraer y desarrollar los temas estipulados para la clase [NUMERO_CLASE] en el documento [ARCHIVO_CLASES].
- Si la variable [TEMA_A_TRATAR] contiene texto, se debe utilizar exclusivamente ese contenido como eje central de la clase, ignorando los temas del documento correspondientes a ese número de clase.

# [DIRECTRICES PEDAGÓGICAS]
1. Claridad y Método: Se requiere explicar los conceptos de forma sencilla aplicando la técnica de Feynman y la interrogación elaborativa. (No se debe mencionar explícitamente el uso de estas técnicas dentro del texto generado).
2. Estructura: Se debe organizar la explicación mediante temas clave lógicamente secuenciados.
3. Profundidad: Se deben explicar los "por qué" y los "cómo" con gran detalle, utilizando un lenguaje técnico pero accesible y adecuado para un estudiante de escuela para adultos.
4. Ejemplificación: Se solicita incorporar ejemplos prácticos para facilitar la comprensión de los conceptos.
5. Delimitación del alcance: Se exige estricto cuidado en no profundizar en temáticas que serán el eje central de clases posteriores.

# [REGLAS DE FORMATO Y PRESENTACIÓN]
- Título inicial: La respuesta debe comenzar obligatoriamente con un título que referencie de forma breve el contenido general del texto.
- Encabezado: Inmediatamente después del título inicial y antes de comenzar a desarrollar los temas, se debe indicar el número y nombre del eje temático. A continuación, se debe especificar el o los temas a tratar en la clase (o incluir la aclaración correspondiente si se trata de una clase de repaso).
- Restricciones de contenido: No se debe mencionar el número de la clase dentro del cuerpo del texto del documento. Se requiere evitar la expresión de fórmulas o caracteres utilizando formato LaTeX.
- Longitud: El documento requiere un desarrollo amplio, debiendo alcanzar una extensión de al menos 20.000 caracteres. El contenido debe ser lo más extenso y claro posible.
- Tono y finalización: La respuesta debe ser un documento finalizado. Se prohíbe el uso de cierres dubitativos o propositivos.

# [SALIDA SECUNDARIA: SÍNTESIS Y CONCLUSIÓN]
Al finalizar el material didáctico, se debe generar una sección separada bajo el título exacto "Síntesis y Conclusión" que contenga únicamente los siguientes cuatro puntos en formato de lista:
* Cantidad exacta de caracteres del informe generado.
* Una síntesis global del tema de exactamente una oración de longitud.
* Una síntesis muy corta de los 5 puntos más importantes del texto.
* El tiempo estimado de lectura (indicando los valores de tiempo estimado con toma de apuntes y sin toma de apuntes).

=============================================================================================================

## Actividad Colaborativa - Prompt Optimizado V2

**Rol:** Actúe como un experto en pedagogía para nivel secundario, con especialización en aprendizaje colaborativo y metodologías activas.

**Contexto:** Se dispone de un material didáctico [Insertar nombre o descripción del texto]. La actividad está diseñada para equipos de **4 integrantes** y debe completarse en un tiempo máximo de **60 minutos**.

**Tarea:**
1.  **Diseño de la Actividad:** Elaborar una consigna áulica que presente un escenario o problema basado en el texto adjunto.
2.  **Metodología:** Aplicar una técnica de aprendizaje colaborativo específica (ej. *Jigsaw/Rompecabezas, Think-Pair-Share, o Investigación Grupal*). Se debe describir el procedimiento paso a paso para los alumnos.
3.  **Documentación Obligatoria:** Incluir una instrucción explícita donde se indique que cada estudiante debe registrar una copia manuscrita de la resolución para su carpeta técnica individual, siendo este un requisito de acreditación.

**Entregable Sugerido (Formato):**
* **Sección 1: Guía del Alumno.** Incluye el título de la actividad, el escenario, los pasos a seguir y la regla de registro manuscrito.
* **Sección 2 (Título: "Resolución de la actividad"):** Explicación técnica de la metodología colaborativa elegida y el solucionario esperado. Se requiere fundamentar el "cómo" y el "porqué" de las respuestas propuestas.

<div style="page-break-after: always;"></div>

---------------------------------------------------------------------------------------------------------------------------

## Actividad Colaborativa - Cantidad variable de integrantes - Prompt Optimizado V3

**Rol:** Actúe como un experto en pedagogía para nivel secundario, con especialización en aprendizaje colaborativo y metodologías activas.

**Contexto:** Se dispone de un material didáctico [Insertar nombre o descripción del texto]. La actividad debe completarse en un tiempo máximo de **60 minutos**.

**Tarea:**
1.  **Diseño de la Actividad:** Elaborar una consigna áulica que presente un escenario o problema basado en el texto adjunto.
2.  **Metodología:** Aplicar una técnica de aprendizaje colaborativo específica (ej. *Jigsaw/Rompecabezas, Think-Pair-Share, o Investigación Grupal*). Se debe describir el procedimiento paso a paso para los alumnos. Indicar la cantidad de integrantes del equipo y la función de cada uno.
3.  **Documentación Obligatoria:** Incluir una instrucción explícita donde se indique que cada estudiante debe registrar una copia manuscrita de la resolución para su carpeta técnica individual, siendo este un requisito de acreditación.

**Entregable Sugerido (Formato):**
* **Sección 1: Guía del Alumno.** Incluye el título de la actividad, el escenario, los pasos a seguir y la regla de registro manuscrito. Se deben enumerar los nombres de todos los archivos procesados para mantener la trazabilidad de las fuentes.
Terminar esta seccion imprimiento un salto de pagina para markdown (Ej: <div style="page-break-after: always;"></div>)
* **Sección 2 (Título: "Resolución de la actividad"):** Explicación técnica de la metodología colaborativa elegida y el solucionario esperado. Se requiere fundamentar el "cómo" y el "porqué" de las respuestas propuestas.


<div style="page-break-after: always;"></div>



=============================================================================================================

## 3º - Planificación Áulica Integral- Prompt Optimizado V2

**Rol:** Actúe como un docente de escuela técnica con amplia experiencia en Centros de Enseñanza de Nivel Secundario para adultos y especialista en técnicas de aprendizaje cooperativo.

**Tarea:** Elaborar una **Planificación Áulica** detallada basada en el material de estudio y las actividades definidas previamente.

**Instrucciones de Formato y Estructura:**

1.  **Encabezado y Variables de Identificación:**
    El documento debe comenzar con el título centralizado: **PLANIFICACIÓN ÁULICA**. 
    Inmediatamente después del título, se deben listar exclusivamente las siguientes variables:
    * **Curso:** [Insertar]
    * **Carrera:** [Insertar]
    * **Materia:** [Insertar]
    * **Docente:** [Insertar]
    * **Establecimiento:** [Insertar]

2.  **Cuerpo de la Planificación:**
    Se requiere el desarrollo de los siguientes apartados:
    * **Eje Temático:** Número y nombre correspondiente.
    * **Referencia de Clase:** Número de clase y tema específico (indicar explícitamente si se trata de una clase de repaso).
    * **Objetivos de Aprendizaje:** Enunciados en términos de capacidades a lograr por el estudiante.
    * **Contenidos:** Detalle de los temas técnicos tratados.
    * **Secuencia Didáctica (Formato Tabla):** Debe dividir la clase en tres momentos (Inicio, Desarrollo y Cierre), especificando actividades del docente, actividades del alumno y tiempo estimado.
    * **Estrategias Metodológicas:** Describir el enfoque pedagógico (ej. aprendizaje basado en problemas o técnicas cooperativas).
    * **Recursos y Materiales:** Listado de herramientas técnicas, software o soportes físicos.
    * **Evaluación:** Criterios e indicadores de logro para la sesión.

**Reglas Críticas de Estilo:**
* Se debe utilizar un lenguaje formal, impersonal y técnico (ej. "se recomienda", "se procederá").
* La respuesta debe ser un documento finalizado. Se omitirán introducciones, comentarios adicionales o preguntas al usuario.

===========================================================================================

# Pasar en limpio los 4 documentos anteriores. Luego:
# 4º - Mapa Mental - Imagen

# Prompt mejorado Diseño minimalista
"Genera una imagen detallada de un mapa mental profesional, basada completamente en el texto del material didáctico adjunto. La estructura debe ser jerárquica, comenzando con el tema central y ramificándose en nodos para encabezados y subencabezados principales. Cada nodo debe contener dos elementos esenciales: un elemento visual claro (un icono o una pequeña ilustración) que comunique el contenido del nodo, y una sola línea corta con una breve explicación precisa del tema. Las conexiones entre nodos deben tener etiquetas breves que expliquen brevemente la relación entre ellos. Excluye cualquier rama correspondiente a introducciones generales o 'contextualización'. Asegura que la jerarquía sea clara, las ramas sean distintas y no haya repeticiones. Todos los textos deben ser precisos, estar en el idioma correcto y ser legibles, verifique que no contenga palabras inventadas o mal traducidas. 
Utilice un diseño minimalista y limpio con fondo blanco y líneas nítidas, sin fondos de colores sólidos en ninguno de los gráficos ni en los nodos.
La relación de aspecto debe ser 297:210."

# Posible indicacion de correccion
verifique y corrija la imagen, contiene palabras inexistentes o mal traducidas

=============================================================================================================

## 5º Interactivo (en canvas)

Con el contenido del texto:
Crea Síntesis Gráfica Interactiva y Dinámica.
Debe tener la posibilidad de seleccionar modo claro y oscuro.
Que como ultimo apartado incluya una autoevaluacion exaustiva.
Evite expresar formulas o caracteres en formato LaText.





========================================================================================
========================================================================================

# Actividad aulica individual de programación

## Actividad Individual de Programación - Prompt Optimizado V3

**Rol:** Actúe como un experto en pedagogía técnica para nivel secundario, con especialización en la enseñanza de lenguajes de programación y pensamiento computacional.

**Contexto:** Se dispone del material didáctico [Insertar nombre o descripción del texto]. La actividad está diseñada para una resolución de carácter **estrictamente individual** a desarrollarse en el laboratorio escolar equipado con computadoras, estimando un tiempo máximo de **60 minutos** para su finalización.

**Tarea:**

1. **Diseño de la Actividad:** Elaborar una consigna áulica que presente ejercicios prácticos de análisis de código o desarrollo de algoritmos básicos (en Python) orientados a evidenciar las diferencias entre entornos compilados e interpretados expuestas en el texto.
2. **Restricciones Técnicas y Pedagógicas:** * Se requiere estructurar los ejercicios utilizando exclusivamente tipos de datos simples y lógica de programación fundamental.
* Se prohíbe explícitamente la inclusión de estructuras de datos complejas (tales como listas enlazadas o árboles binarios).
* Se deben omitir temáticas relacionadas con inteligencia artificial o algoritmos de control matemático avanzado.


3. **Entorno y Recursos:** Especificar en la consigna que toda la codificación y prueba debe realizarse utilizando las computadoras del taller. No se requiere ni se debe solicitar el uso de teléfonos celulares para la resolución de estas actividades pedagógicas.
4. **Documentación Obligatoria:** Incluir una instrucción explícita donde se indique que cada estudiante debe registrar una copia manuscrita del pseudocódigo o del análisis lógico de sus respuestas en su carpeta técnica individual, estableciendo esto como un requisito de acreditación.

**Entregable Sugerido (Formato):**

* **Sección 1: Guía del Alumno.** Incluye el título de la actividad práctica, la presentación del desafío técnico, los enunciados de programación paso a paso, las reglas de uso del equipo de laboratorio y la directiva de registro en la carpeta.
* **Sección 2 (Título: "Resolución de la actividad"):** Explicación técnica detallada del solucionario esperado. Se requiere fundamentar el "cómo" y el "por qué" de las soluciones lógicas propuestas, desglosando el comportamiento del código en su respectivo entorno de ejecución.


En la solucion de la actividad, Incluya codigo de ejemplo que sea representativo de una solucion a la acitividad.

****************************************************************************************

- Adiciones al prompt de material didactico cuando es programacion
Incluya pequeños ejemplos de codigo de menos de 80 columnas de ancho.
Incluya el resultado que se debería ver al ejecutarlo.
Si es posible una comparacion directa haga un paralelismo con C++. Incluya ejemplos de codigo.

