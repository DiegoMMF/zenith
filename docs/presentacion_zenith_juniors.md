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

## 8. Directrices para Contribuir al Código de Zenith

Si algún desarrollador necesita hacer cambios en el motor de Zenith (`zenith/src/zenith_harness/`), debe seguir estas directrices dictadas por `AGENTS.md`:

* **Estilo y Tipado:** Usar tipado estricto de Python (`mypy`), Modelos Pydantic para los datos, y un límite estricto de 100 caracteres por línea regulado por **Ruff**.
* **Pruebas (Testing):** Los tests corren sobre `pytest-asyncio`. Se debe priorizar "mockear" (simular) el comportamiento del `Dispatcher` para pruebas rápidas. Las pruebas reales (*smoke tests*) que levantan agentes externos se ejecutan solo bajo demanda mediante variables de entorno.
