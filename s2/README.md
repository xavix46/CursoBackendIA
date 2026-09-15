## Clase 2 — APIs de IA Generativa y memoria conversacional

### Conversación de 8 turnos (Paso 7)

Ver evidencia en `entregas/s02/evidencia/memoria.png`.

Hola, Alex. ¡Un gusto! El verde es un color excelente.
Como soy una inteligencia artificial general, no tengo acceso al historial de tus clases específicas. ¿Podrías decirme el contexto o el tema de tu curso para ayudarte a identificarlo?
Un número decimal con parte fraccionaria, como **3.14**, o un número entero extremadamente grande que supere el límite de memoria asignado (aunque en Python los `int` tienen precisión arbitraria, conceptualmente no caben en un `int` de lenguaje de bajo nivel como C).
El comando `uv init` inicializa un nuevo proyecto de Python en el directorio actual. Crea los archivos de configuración básicos, como el `pyproject.toml`, necesarios para gestionar dependencias y el entorno del proyecto utilizando la herramienta `uv`.
Un token es la unidad básica de texto, equivalente a una palabra, parte de ella o un signo de puntuación, que las IA utilizan para procesar y generar información.Que una API sea *stateless* significa que el servidor no guarda información sobre el estado del cliente entre peticiones; cada solicitud debe contener toda la información necesaria para ser procesada.
Un archivo `.env` sirve para almacenar variables de configuración y datos confidenciales, como contraseñas o claves de API, fuera del código fuente.
Te llamas Alex y tu color favorito es el verde.

### Por qué elegí ventana deslizante

Elegí ventana deslizante porque es económica en tokens y perfecta para conversaciones cortas: los últimos 10 turnos cubren los 8 necesarios sin perder contexto. Es más simple que resumen progresivo o almacenamiento externo, y ideal para demostrar el problema del olvido que resuelve reinviar historial.

### Límite de solicitudes provocado (Paso 9)

Ver evidencia en `entregas/s02/evidencia/rate_limit.png`.

* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20, model: gemini-3.5-flash
Please retry in 43.650523131s.. No se reintenta.