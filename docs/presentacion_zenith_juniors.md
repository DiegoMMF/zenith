# 🚀 Conociendo Zenith: Orquestación Multi-Agente para Tareas Complejas

Documento elaborado para introducir a los desarrolladores Junior en el uso y potencial de **Zenith**.

---

## 1. ¿Qué es Zenith?

**Zenith** es un "harness" (entorno de ejecución o arnés) diseñado para transformar agentes de IA de programación convencionales (como *Claude Code* o *Codex*) en un sofisticado **orquestador multi-agente**.

A través de los protocolos **MCP** (Model Context Protocol) y **ACP** (Agent Client Protocol), Zenith toma el control de un agente principal y le permite delegar trabajo a "sub-agentes" (workers y testers), revisar los avances, registrar habilidades reutilizables y replanificar continuamente hasta que una tarea esté verdaderamente terminada.

## 2. El Problema que Resuelve y su Potencial

El principal problema que tienen los agentes autónomos de programación es que **se rinden o se detienen de forma prematura** antes de resolver un proyecto largo, no porque no sepan hacerlo, sino porque pierden el hilo ("premature completion").

> [!TIP]
> **El gran logro de Zenith:**
> Según el reporte técnico, Zenith obliga al agente a realizar un proceso adaptativo donde evalúa repetidamente la brecha entre el código actual y los requisitos originales. Esto lo posiciona en el **puesto #1 global del Frontier SWE Benchmark** con GPT-5.5, utilizando menos de la mitad del presupuesto (USD por tarea) que otras alternativas como RALPH.

## 3. ¿Por qué usar Zenith en lugar de abrir varias sesiones manualmente?

Es normal preguntarse por qué no simplemente abrir nosotros mismos varias ventanas de chat con nuestro modelo favorito. La diferencia radica en la carga cognitiva:

* **Si lo haces manual:** Tú eres el Project Manager, el que integra el código, el que revisa, y el que tiene que recordar todo el contexto. Tienes que repartir tareas, evitar solapamientos y decidir si la tarea está lista.
* **Con Zenith:** Tú solo das la misión. El agente orquestador (manejado por Zenith) asume el rol de PM: divide la misión en tareas (creando un "grafo" de dependencias), lanza trabajadores paralelos con contexto limpio, y envía "validadores" independientes a revisar el código.

> [!WARNING]
> **La desventaja a considerar:** Añade fricción. Para un cambio de 2 líneas de código, Zenith agrega una "ceremonia" innecesaria. Es una herramienta estricta pensada para tareas largas donde hay riesgo de dañar la base de código si no se tiene una disciplina de pasos de control.

## 4. Casos de Uso Sugeridos

Para el día a día de un equipo de desarrollo, Zenith brilla en:

* **Tareas de programación de "Largo Aliento" (Long-horizon tasks):** Implementaciones pesadas como migraciones de código, refactorizaciones a gran escala o desarrollo de un feature complejo desde cero, que normalmente tomarían semanas.
* **Verificación Independiente de Código:** Zenith puede orquestar que un agente escriba el código y automáticamente lanzar un agente "tester" independiente que revise y retroalimente al trabajador si algo falla.
* **Descubrimiento y automatización (Skills):** A medida que los sub-agentes descubren cómo hacer cosas en tu repositorio, pueden guardarlas como "habilidades" (skills) para no tener que razonar desde cero la próxima vez.

## 5. Arquitectura Interna (La magia detrás del telón)

Para entender verdaderamente Zenith, hay que ver sus componentes internos (`CLAUDE.md`):

* **No es un agente en sí mismo, es un Servidor MCP.** Cuando inicializas Zenith, le inyecta 7 "herramientas" especiales al agente anfitrión (Claude o Codex) para darle sus poderes de orquestación.
* **El Coordinador y la Máquina de Estados:** El núcleo es un *state-machine* que transiciona de planificación a ejecución. A partir de ahí, un `Dispatcher` lanza procesos ACP en paralelo (hasta 4 por defecto).
* **Memoria en Disco:** El controlador no guarda la memoria temporalmente en RAM; todo se guarda de forma duradera en una base local dentro de `$ZENITH_HOME/projects/`. Si tu computadora se apaga, la misión se reanuda desde el último estado en disco.

## 6. Compatibilidad Real: Herramientas y Modelos

Es importante conocer los límites actuales de la herramienta:

* **CLIs Soportados (Orquestadores):** Oficialmente, Zenith solo soporta **Claude Code** y **Codex** como terminales anfitrionas. Integrar otras herramientas (como OpenCode o Antigravity) requeriría modificar el código fuente (`providers.py`) y crear adaptadores ACP.
* **Modelos Soportados:** Aunque Zenith maneja las interfaces de Claude y Codex, puedes utilizar el "cerebro" de otros modelos (como GLM-5.2, DeepSeek V4 Pro, Gemini) **indirectamente**. Esto se hace mediante variables de entorno (ej. cambiando `ANTHROPIC_BASE_URL` para apuntar a un proxy, o definiendo `GLM_BASE_URL`) que reenvían las peticiones de la terminal al modelo deseado.

## 7. 🛠️ Guía de Implementación Paso a Paso

A continuación, los pasos para usar Zenith en proyectos diarios:

### Paso A: Requisitos Previos

Asegúrense de tener instalado en su máquina:

* **Python 3.11+**
* [**uv**](https://docs.astral.sh/uv/) (el gestor de paquetes de Python)
* **Node.js 22+** y `npm`
* CLI de agentes (Claude Code o Codex)

### Paso B: Instalación de Zenith

Abran una terminal dentro del repositorio fuente de `zenith` y corran:

```bash
# Sincronizar dependencias
uv sync

# Verificar que el CLI de zenith quedó instalado
uv run zenith --help
```

Instalen globalmente los adaptadores ACP (Workers/Validators) para los agentes que quieran
tener disponibles. Pueden instalar **Claude Code y Codex al mismo tiempo**: no se pisan entre
sí, porque solo agregan comandos distintos al sistema (`claude-agent-acp` y `codex-acp`). La
elección de cuál usar se hace después, al inicializar Zenith para cada proyecto o al configurar
qué proveedor usará cada rol.

```bash
# Adaptador para Claude
npm install -g @agentclientprotocol/claude-agent-acp

# Adaptador para Codex
npm install -g @agentclientprotocol/codex-acp
```

### Paso C: Inicializar Zenith en su Proyecto Objetivo

Tienen que decirle a Zenith qué proyecto van a intervenir. Desde el repositorio fuente de Zenith, ejecuten este comando apuntando a la ruta de *su repositorio de trabajo*:

```bash
uv run zenith init --workspace-dir /ruta/a/mi-proyecto --agent claude
```

Si prefieren usar Codex para ese proyecto, cambien el agente:

```bash
uv run zenith init --workspace-dir /ruta/a/mi-proyecto --agent codex
```

También se pueden combinar roles. Por ejemplo, Claude como orquestador y Codex como worker o
validador:

```bash
uv run zenith init \
  --workspace-dir /ruta/a/mi-proyecto \
  --orchestrator-provider claude \
  --worker-provider codex \
  --validator-provider codex
```

> [!NOTE]
> Este comando no modifica su código, pero inyecta los archivos necesarios para el agente
> elegido (por ejemplo, `.claude/orchestrator_prompt.md` o `.codex/orchestrator_prompt.md`)
> y configura el entorno para que reciba los poderes de orquestador.

### Paso D: Iniciar la Misión

Diríjanse a la carpeta de *su proyecto objetivo*, levanten la terminal del agente y pasen el mando:

```bash
cd /ruta/a/mi-proyecto
claude
# o, si inicializaron el proyecto para Codex:
codex
```

**Denle el contexto y la misión con el siguiente prompt:**

```text
First read .claude/orchestrator_prompt.md and treat it as your primary role, then use Zenith to run this mission.

<Aquí escriben el requerimiento complejo que necesitan programar>
```

Si están usando Codex como orquestador, el prompt cambia solo en la ruta:

```text
First read .codex/orchestrator_prompt.md and treat it as your primary role, then use Zenith to run this mission.

<Aquí escriben el requerimiento complejo que necesitan programar>
```

## 8. Continuar un Proyecto y Cambio de Agentes (Resilience & Handoff)

Es común que una tarea agote los tokens o créditos de un agente (ej. límite de horas). Si esto ocurre, puedes retomar el mismo proyecto exacto, **incluso usando otro agente distinto** (por ejemplo, pasándote de Codex a Claude).

### ¿Cómo funciona el almacenamiento de Zenith?

Cuando usas `zenith init --agent codex`, solo preparas tu carpeta local (instalando configuraciones de arranque). El proyecto *real* de Zenith (tareas, estado, intentos) **se crea recién al iniciar el agente** y cuando éste ejecuta la herramienta `start_project`. Esto genera un "bucket" de almacenamiento agnóstico al agente, guardado globalmente en `$ZENITH_HOME/projects/<project_id>/`.

Si simplemente inicializas Claude y le dices "continúa", por defecto el orquestador llamará a `start_project` y **creará un proyecto nuevo** desde cero (generando un ID nuevo). Ambos agentes operarán sobre tu mismo código local, pero tendrán listas de tareas de Zenith completamente independientes.

### Cómo retomar el proyecto exacto (Handoff)

Para que un agente continúe exactamente el trabajo y las tareas donde se quedó el anterior:

1. **Busca el ID original:** Ejecuta `uv run zenith list-projects` y copia el ID del proyecto en el que estabas trabajando (ej. `20260630T...-project`).
2. **Prepara el entorno para el nuevo agente:** Ejecuta `uv run zenith init --workspace-dir /ruta/a/mi-proyecto --agent claude`.
3. **Pasa el mando:** Inicia Claude y dile explícitamente en tu primer prompt:
   > First Read the .antigravity/orchestrator_prompt.md and treat it as your primary role, then use Zenith to run this mission.
   >
   > *"Quiero que retomes un proyecto de Zenith existente. El ID del proyecto es **`<pega_aqui_el_id>`**. Por favor, utiliza tu herramienta `inspect_project` pasando este ID para ver el estado actual, las tareas pendientes y la memoria del proyecto, y luego continúa la ejecución llamando a `advance_project`."*

De esta forma, Claude (o el agente que elijas) se conectará al mismo "bucket" y retomará el árbol de tareas de forma transparente.

## 9. Recomendaciones de Modelos (Setup Ideal para Economizar)

> [!NOTE]
> Verificado el **30 de junio de 2026**. Esta parte cambia rápido: antes de fijar un
> presupuesto real, revisen los precios y límites actuales del proveedor que vayan a usar.

Si lo que buscan es buen costo-beneficio para programación mediante agentes, a mediados de
2026 conviene pensar menos en "un modelo ganador" y más en **qué rol cumple cada modelo**:
planificación, escritura masiva de código, validación independiente o ejecución barata de
muchos intentos.

### 1. Arquitectura y tareas largas: GLM-5.2

**GLM-5.2** es una opción fuerte para tareas largas de arquitectura y coordinación. La ficha
de Hugging Face de Z.ai lista **753B parámetros**, licencia **MIT**, soporte de **1M tokens de
contexto** y foco explícito en tareas "long-horizon". No lo traten como "barato para todo":
su valor está en sostener contexto amplio y planificación de alto nivel.

### 2. Costo-beneficio general: DeepSeek V4 Pro / Flash

**DeepSeek V4** es una de las mejores opciones cuando el costo importa. La documentación
oficial publica dos variantes:

* **DeepSeek V4 Flash:** 284B parámetros totales / 13B activos, 1M de contexto, tool calling,
  JSON mode y precio oficial de **USD 0.14 input / USD 0.28 output por millón de tokens**.
* **DeepSeek V4 Pro:** 1.6T parámetros totales / 49B activos, 1M de contexto, orientado a
  razonamiento y agentes, con precio oficial de **USD 0.435 input / USD 0.87 output por
  millón de tokens** en la API directa de DeepSeek.

Para Zenith, **Flash** encaja muy bien como worker/validator barato; **Pro** tiene más sentido
cuando el sub-agente debe razonar bastante antes de tocar código.

### 3. Tool calling y agentes de código: Qwen

La familia **Qwen** sigue siendo muy relevante para flujos agénticos. Qwen documenta
**Qwen3-Coder-480B-A35B-Instruct** con 256K de contexto nativo, extensión hasta 1M con YaRN,
Qwen Code como CLI, integración con Claude Code mediante proxy y buen soporte de tool use.
Además, OpenCode Go expone modelos Qwen recientes, como **Qwen3.7 Max**, **Qwen3.7 Plus** y
**Qwen3.6 Plus**.

Recomendación práctica: usen Qwen cuando necesiten muchos tool calls, edición de repositorio
y compatibilidad con CLIs, pero validen en su propio proyecto porque la calidad depende mucho
del proveedor que sirve el modelo y de la configuración del agente.

### 4. Velocidad e iteración: Kimi K2.7 Code

**Kimi K2.7 Code** está documentado en la plataforma de Kimi como su modelo de coding más
capaz, con **256K de contexto**, soporte multimodal, tool calls, JSON mode, thinking mode y
una variante **HighSpeed** que apunta a mayor velocidad de salida. Es buena alternativa para
workers que necesitan avanzar rápido, especialmente cuando se usa detrás de una API
OpenAI-compatible.

---

### 💡 Mi recomendación de Setup para Zenith

Puesto que con Zenith dividimos el trabajo entre el **orquestador** y los **workers /
validators**, lo más inteligente para ahorrar dinero es usar un **sistema de ruteo mixto**:

1. **Orquestador:** usar **GLM-5.2**, **DeepSeek V4 Pro**, **Claude Opus/Sonnet** o **GPT-5
   Codex** si el trabajo exige mucha planificación, revisión de requisitos o retención de
   contexto. En esta capa conviene pagar más si evita malas decisiones arquitectónicas.
2. **Workers:** usar **DeepSeek V4 Flash**, **Kimi K2.7 Code HighSpeed** o **Qwen3.7 Plus /
   Qwen3-Coder**. Aquí se queman la mayoría de los tokens, así que prioricen precio,
   velocidad y buena edición de código.
3. **Validators:** no usen siempre el mismo modelo que escribió el código. Si el worker fue
   DeepSeek Flash, prueben validar con Qwen/Kimi/Claude Haiku/Sonnet; la diversidad reduce
   puntos ciegos.
4. **Tareas críticas:** para cambios de seguridad, migraciones de datos, auth, pagos o
   infraestructura, suban temporalmente la calidad del validator aunque sea más caro.
5. **Proyectos grandes:** activen caché de contexto cuando el proveedor la cobre barato. En
   flujos con mucho repo repetido, el cache hit puede cambiar más el costo final que el precio
   nominal del modelo.

> [!TIP]
> **OpenCode Go como opción económica:** esta rama de Zenith ya incluye provider `opencode`
> (`opencode acp`). OpenCode Go cuesta **USD 5 el primer mes y luego USD 10/mes**, e incluye
> GLM-5.2, DeepSeek V4 Pro/Flash, Kimi K2.7 Code y Qwen recientes. Pero no es una tarifa plana
> ilimitada: la documentación oficial define límites por valor de uso (**USD 12 cada 5 horas,
> USD 30 semanal y USD 60 mensual**) y permite usar saldo adicional si se habilita. Es muy
> atractivo para juniors o pruebas intensivas, pero no prometan "costo marginal cero" para uso
> sin límites.

### Checklist para elegir modelo antes de lanzar una misión

Antes de lanzar Zenith, definan:

* **Presupuesto máximo:** costo por hora o por misión, no solo por millón de tokens.
* **Contexto necesario:** 128K alcanza para tareas chicas; 256K-1M sirve para repos grandes,
  auditorías y migraciones.
* **Herramientas:** confirmar tool calling, JSON mode, FIM si van a editar código, y soporte
  ACP/CLI real.
* **Latencia:** para workers paralelos, un modelo algo menos inteligente pero mucho más rápido
  puede terminar antes y costar menos.
* **Privacidad:** revisar retención de datos, región de hosting y si el proveedor usa prompts
  para entrenamiento.
* **Plan B:** tener un modelo alternativo configurado para cuando haya rate limits, caídas o
  degradación de calidad.

Fuentes consultadas: [GLM-5.2 en Hugging Face](https://huggingface.co/zai-org/GLM-5.2),
[DeepSeek V4 Preview](https://api-docs.deepseek.com/news/news260424),
[precios oficiales de DeepSeek](https://api-docs.deepseek.com/quick_start/pricing),
[Qwen3-Coder](https://qwenlm.github.io/blog/qwen3-coder/),
[Kimi K2.7 Code](https://platform.kimi.ai/docs/guide/kimi-k2-7-code-quickstart),
[OpenCode Go](https://opencode.ai/docs/go/).
