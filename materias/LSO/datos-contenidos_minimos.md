### 1. Fundamentos de Arquitectura y .NET

* **Introducción a C# y Minimal APIs:** Se configuran proyectos web ligeros mediante .NET, estableciendo la estructura de archivos, el punto de entrada y la gestión del contenedor de dependencias (`WebApplicationBuilder`).
* **Enrutamiento y Endpoints:** Se definen rutas mediante métodos HTTP (`GET`, `POST`, `PUT`, `DELETE`) para la exposición directa de servicios sin la complejidad de controladores tradicionales.

### 2. Procesamiento de Datos y Lógica de Negocio

* **Modelos y Transferencia de Datos:** Se diseñan clases de entidades y objetos de transferencia de datos (DTOs) para estructurar la información recibida y enviada por la API.
* **Validación y Manejo de Errores:** Se implementan mecanismos de validación de entradas y manejo centralizado de excepciones para asegurar la robustez de las respuestas HTTP.

### 3. Persistencia de Datos con SQL Server y ORM

* **Conexión y Mapeo Objeto-Relacional:** Se configura la conexión a bases de datos SQL Server utilizando Entity Framework Core para el mapeo de tablas a modelos de C#.
* **Operaciones CRUD y Consultas:** Se ejecutan consultas y operaciones de persistencia mediante LINQ y métodos asíncronos (`async/await`) para garantizar la eficiencia transaccional.

### 4. Documentación, Seguridad y Pruebas

* **Documentación de Servicios:** Se integra Swagger/OpenAPI para la especificación visual y prueba interactiva de los endpoints desarrollados.
* **Seguridad y Pruebas de Endpoints:** Se configuran políticas básicas de autenticación/autorización y se realizan pruebas funcionales de los servicios expuestos.