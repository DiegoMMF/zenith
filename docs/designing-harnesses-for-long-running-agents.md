# Resumen del documento "From RALPH to Zenith: Designing Harnesses for Long-Running Agents"

El documento que leí es un informe técnico titulado **"From RALPH to Zenith: Designing Harnesses for Long-Running Agents"** (De RALPH a Zenith: Diseñando entornos para agentes de ejecución larga), escrito por la organización *Intelligent Internet*.

Se trata de un estudio profundo sobre cómo diseñar la "arquitectura" o "entorno" (harness) que controla a un agente de Inteligencia Artificial para que pueda resolver **tareas de largo horizonte** (aquellas complejas que toman mucho tiempo, requieren múltiples pasos y donde es fácil perder el hilo o creer erróneamente que se ha terminado).

Aquí tienes los puntos clave de lo que aborda:

## 1. El problema principal

El estudio parte de la base de que los agentes a menudo fallan en tareas largas no porque no puedan avanzar, sino porque se detienen antes de que la tarea esté verdaderamente terminada (completitud prematura). Para solucionarlo, evalúan la evolución de 5 diseños de control en 8 tareas de alta complejidad (como programar un juego de físicas, crear una app de escritorio completa, reimplementar Git en lenguaje Zig o reproducir papers de Machine Learning).

## 2. La evolución de las 5 arquitecturas

El documento relata cómo cada diseño soluciona un problema del anterior, pero introduce uno nuevo:

1. **One-session (Una sola sesión):** El agente hace todo de corrido. Es el más barato, pero falla mucho porque el mismo agente que escribe el código decide que ya terminó, volviéndose excesivamente confiado.
2. **RALPH:** Obliga al agente a detenerse, reabrir los requisitos originales y buscar "brechas" de lo que falta hacer en un bucle continuo. Es muy potente (escribe código mucho mejor iterando) pero es **el más caro** y no tiene una regla clara de cuándo parar.
3. **Plan-RALPH:** En lugar de buscar errores a ciegas, crea una lista de tareas al principio y las va tachando. Es más barato, pero es frágil porque el plan queda obsoleto rápido y los agentes a veces marcan tareas como "hechas" cuando en realidad fallan en el contexto general.
4. **Milestone-RALPH:** Divide el trabajo en "hitos" y solo planea el hito actual. Lo más importante: introduce un **probador independiente**. El hito no se aprueba porque el trabajador diga que terminó, sino porque un "tester" independiente no logra encontrarle fallas.
5. **Zenith (El ganador):** Es la culminación del estudio. Mantiene los hitos pero hace que la orquestación sea **dinámica y adaptativa**. El sistema puede cambiar en tiempo real a los trabajadores (ej. asignar un agente experto en frontend y otro en lógica), cambiar a los testers, crear "habilidades" reutilizables para no cometer el mismo error dos veces y decidir de forma inteligente cuándo parar.

## 3. Conclusiones y Costos

* **Zenith** demostró ser el mejor enfoque, logrando el rango de éxito más alto de todos y costando **menos de la mitad** en cómputo que el enfoque de fuerza bruta de RALPH.
* El documento concluye que para las tareas complejas de IA, el secreto no es simplemente "gastar más dinero en cómputo/tokens", sino que el gasto debe estar **controlado y dirigido**: pruebas en capas, roles adaptativos y revisión inteligente del estado del proyecto.

En resumen, es un paper fundamental sobre ingeniería de agentes, argumentando que a medida que los modelos de IA son más potentes, la forma en que los orquestamos, verificamos y planificamos (el "harness") es lo que define si pueden completar un proyecto de software masivo por sí solos o no.

---

## GLM vs GPT/Claude

Si el presupuesto es estricto y tu trabajo es muy analítico/investigativo, GLM-5.2 a 16 USD es fenomenal. Sin embargo, por una mínima diferencia de 4 USD, Claude Code o ChatGPT Códex te entregarán una herramienta mucho más robusta y completa para el desarrollo de software diario.

Mucha gente de hecho está optando por flujos "híbridos": usar modelos baratos para investigación, y pagar la suscripción de 20 USD para que Opus o GPT-5.5 hagan la implementación pesada.

Eso, si pensamos únicamente en el escenario de una **suscripción mensual fija para un usuario final**, pero la ecuación cambia drásticamente cuando hablamos de **consumo por API (pago por token)** y escalabilidad, que es el verdadero "rendimiento" económico para proyectos serios o agentes autónomos.

Si analizamos el **rendimiento por dólar invertido**, GLM-5.2 destroza a sus competidores norteamericanos. Aquí te explico por qué este factor lo cambia todo:

### 1. El costo brutal de los agentes de largo alcance

Herramientas como el *harness* de Zenith, Claude Code o agentes autónomos funcionan enviando iteraciones masivas al modelo. No es un "pregunta y respuesta" simple; el modelo lee cientos de archivos, planea, ejecuta y verifica en un bucle que consume **millones de tokens por tarea**.

* En los modelos frontera de EE.UU. (como Claude Opus 4.8 o GPT-5.5), correr una tarea compleja puede costar fácilmente entre **$5 y $20 USD solo en consumo de API**.
* En GLM-5.2, al ser entre **5 y 10 veces más barato** (promediando $1.40 USD por cada millón de tokens de entrada), esa misma tarea puede costarte céntimos o, a lo sumo, un par de dólares.

### 2. La ventaja de la "Fuerza Bruta Cognitiva"

Dado que GLM-5.2 es tan económico, te permite compensar esa ligera desventaja en "implementación" o "inteligencia pura" que vimos en el benchmark mediante estrategias que serían prohibitivas con modelos de OpenAI o Anthropic:

* **Múltiples reintentos:** Puedes decirle a GLM-5.2 que intente resolver un problema de 5 formas distintas, evalúe las 5, y se quede con la mejor. Hacer esto con GPT-5.5 te costaría una fortuna; con GLM es viable.
* **Contextos inmensos:** Puedes pasarle historiales de código completos, repositorios enteros o logs masivos de errores sin preocuparte por la factura a fin de mes.

### 3. Rentabilidad para startups y despliegues masivos

Si estás automatizando flujos de trabajo (por ejemplo, un agente que revisa los *Pull Requests* de todo tu equipo, o que actualiza dependencias masivamente), pagar los costos de API de Claude o OpenAI no es escalable. Aquí es donde el ecosistema chino brilla: te ofrecen un modelo "suficientemente bueno" (que de hecho es el #4 global y el #1 en investigación) a un costo que permite ponerlo a trabajar 24/7.

**En conclusión:**
Si vas a consumir el modelo mediante **API o para agentes autónomos intensivos** (como Zenith), tu observación es 100% correcta. El rendimiento precio/calidad de GLM-5.2 es imbatible. Te entrega quizá un 85-90% de la capacidad de GPT-5.5 por una fracción minúscula del precio, permitiéndote escalar la inteligencia artificial en tus proyectos de una forma que hoy por hoy es impensable económicamente con los modelos líderes de occidente.
