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

* **No es un agente en sí mismo, es un Servidor MCP.** Cuando inicializas Zenith, le inyecta 7 "herramientas" especiales al agente anfitrión (por ejemplo, Claude, Codex, OpenCode o Antigravity) para darle sus poderes de orquestación.
* **El Coordinador y la Máquina de Estados:** El núcleo es un *state-machine* que transiciona de planificación a ejecución. A partir de ahí, un `Dispatcher` lanza procesos ACP en paralelo (hasta 4 por defecto).
* **Memoria en Disco:** El controlador no guarda la memoria temporalmente en RAM; todo se guarda de forma duradera en una base local dentro de `$ZENITH_HOME/projects/`. Si tu computadora se apaga, la misión se reanuda desde el último estado en disco.

## 6. Compatibilidad Real: Herramientas y Modelos

Es importante conocer los límites actuales de la herramienta:

* **Providers registrados:** el código actual registra `claude`, `codex`, `antigravity` y `opencode` como providers posibles para orquestador y workers.
* **No todos tienen la misma madurez:** Claude y Codex tienen integración más directa. `opencode` está registrado con el comando `opencode acp`. `antigravity` también está registrado, pero el adaptador incluido en este repositorio es un proof-of-concept y no garantiza por sí solo selección real de modelos Gemini.
* **Zenith separa por rol, no por dificultad automática:** puedes configurar orquestador, workers y validators con providers distintos, pero Zenith no decide dinámicamente "esta tarea es simple, uso modelo barato" y "esta tarea es compleja, uso modelo caro". Esa política hoy se logra configurando roles.
* **Modelos vía entorno:** para algunos providers, especialmente Claude, puedes usar variables de entorno para apuntar el orquestador y los sub-agentes a modelos distintos. Zenith reenvía variables como `ANTHROPIC_MODEL`, `CLAUDE_CODE_SUBAGENT_MODEL`, `ANTHROPIC_BASE_URL`, `GLM_BASE_URL`, `ZAI_BASE_URL` y sus claves asociadas.

## 7. 🛠️ Guía de Implementación Paso a Paso

A continuación, los pasos para usar Zenith en proyectos diarios:

### Paso A: Requisitos Previos

Asegúrense de tener instalado en su máquina:

* **Python 3.11+**
* [**uv**](https://docs.astral.sh/uv/) (el gestor de paquetes de Python)
* **Node.js 22+** y `npm`
* CLI de agentes según el provider que quieran usar: Claude Code, Codex, OpenCode o Antigravity

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

Para OpenCode, Zenith espera que exista el comando `opencode acp`. Para Antigravity, el repo
incluye un adaptador de prueba (`python -m agy_acp_server`), pero no debe confundirse con una
integración completa de modelos Gemini.

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
   > First read .claude/orchestrator_prompt.md and treat it as your primary role, then use Zenith to run this mission.
   >
   > *"Quiero que retomes un proyecto de Zenith existente. El ID del proyecto es **`<pega_aqui_el_id>`**. Por favor, utiliza tu herramienta `inspect_project` pasando este ID para ver el estado actual, las tareas pendientes y la memoria del proyecto, y luego continúa la ejecución llamando a `advance_project`."*

Si el nuevo agente es otro, cambia la ruta del prompt:

* Claude: `.claude/orchestrator_prompt.md`
* Codex: `.codex/orchestrator_prompt.md`
* Antigravity: `.antigravity/orchestrator_prompt.md`
* OpenCode: `.opencode/orchestrator_prompt.md`

De esta forma, el agente elegido se conecta al mismo "bucket" y retoma el árbol de tareas de forma transparente.

## 9. Configurar Modelos Caros y Baratos con el Zenith Actual

La idea práctica es simple: usar un modelo más inteligente para el **orquestador** y un modelo
más barato o rápido para **workers / validators**. La implementación concreta depende del
provider.

> [!IMPORTANT]
> Zenith no tiene todavía una opción universal tipo `--orchestrator-model` y
> `--worker-model`. Lo que sigue usa solo la configuración actual del repositorio.

| Provider | Orquestador | Workers / validators | Cómo configurarlo | Límite actual |
| --- | --- | --- | --- | --- |
| `claude` | Modelo definido por `ANTHROPIC_MODEL` | Modelo definido por `CLAUDE_CODE_SUBAGENT_MODEL` | Variables de entorno antes de `zenith init` | Es la ruta más limpia hoy |
| `codex` | `gpt-5.5` queda escrito en `.codex/config.toml` | Puede pasarse por `--worker-acp-command` | Override `codex-acp -c model="..."` | Validators pueden requerir ajuste manual |
| `antigravity` | Depende del CLI/backend externo | Depende del CLI/backend externo | Zenith solo registra el provider | El adaptador incluido es simulado |
| `opencode` | Depende de `opencode acp` | Depende de `opencode acp` | Configuración propia de OpenCode | Zenith no fuerza modelo por rol |

### Caso A: Claude con orquestador Opus y workers Haiku

Este es el caso mejor soportado sin tocar código. Define el modelo del orquestador con
`ANTHROPIC_MODEL` y el de sub-agentes con `CLAUDE_CODE_SUBAGENT_MODEL` antes de inicializar el
workspace:

```bash
cd /ruta/al/repositorio/zenith/zenith

export ANTHROPIC_MODEL="claude-opus-model-id"
export CLAUDE_CODE_SUBAGENT_MODEL="claude-haiku-model-id"

uv run zenith init \
  --workspace-dir /ruta/a/mi-proyecto \
  --agent claude
```

Después inicia Claude desde el proyecto objetivo:

```bash
cd /ruta/a/mi-proyecto
claude
```

Usa los IDs reales que acepte tu instalación de Claude Code. Si apuntas Claude a un proxy o a
un proveedor compatible, también puedes definir `ANTHROPIC_BASE_URL` y las claves necesarias
antes de ejecutar `zenith init`.

### Caso B: Codex con orquestador GPT-5.5 y workers GPT-5.4-mini

El bootstrap actual de Zenith escribe `model = "gpt-5.5"` en `.codex/config.toml`, así que el
orquestador de Codex queda en GPT-5.5 sin hacer nada extra. Para workers, usa
`--worker-acp-command`:

```bash
cd /ruta/al/repositorio/zenith/zenith

uv run zenith init \
  --workspace-dir /ruta/a/mi-proyecto \
  --agent codex \
  --worker-acp-command 'codex-acp -c model="gpt-5.4-mini"'
```

Esto configura:

* **Orquestador:** GPT-5.5, por el `model` generado en `.codex/config.toml`.
* **Workers:** GPT-5.4-mini, por el override del comando ACP.

Si también quieres forzar validators a GPT-5.4-mini y notas que no heredan el comando del
worker, revisa el bloque `[mcp_servers.zenith.env]` en `.codex/config.toml` y agrega o ajusta:

```toml
ZENITH_VALIDATOR_ACP_COMMAND = "codex-acp -c model=\"gpt-5.4-mini\""
```

Este ajuste manual es una limitación del estado actual: Zenith sí separa roles, pero no expone
todavía una opción universal de modelo por rol.

### Caso C: Antigravity con Gemini Pro y Flash

Con el repositorio tal como está, Zenith puede preparar el provider `antigravity`:

```bash
cd /ruta/al/repositorio/zenith/zenith

uv run zenith init \
  --workspace-dir /ruta/a/mi-proyecto \
  --agent antigravity
```

Pero Zenith no puede garantizar por sí solo:

* orquestador en `gemini-3.1-pro`;
* workers en `gemini-3.5-flash`.

La razón es que el adaptador `agy-acp/agy_acp_server.py` incluido aquí responde como prueba de
concepto y no conecta realmente con un selector de modelos Gemini. Para lograr ese ruteo sin
modificar Zenith, debes configurarlo en el propio CLI/backend de Antigravity si expone flags o
variables para modelo principal y modelo de sub-agentes.

### Caso D: OpenCode como alternativa económica

Zenith registra `opencode` y usa `opencode acp` como comando de workers. Puedes inicializarlo
así:

```bash
cd /ruta/al/repositorio/zenith/zenith

uv run zenith init \
  --workspace-dir /ruta/a/mi-proyecto \
  --agent opencode
```

La elección fina de modelos depende de la configuración de OpenCode. Zenith no fuerza todavía
"orquestador caro / workers baratos" para OpenCode desde sus propias opciones.

## 10. Recomendaciones de Modelos (Setup Ideal para Economizar)

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
validators**, lo más inteligente para ahorrar dinero es usar una **configuración mixta por rol**:

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
