# Repository Guidelines

## Project Structure & Module Organization

This repository contains the Zenith technical report and the Python harness package.
The package lives in `zenith/`.

- `README.md`: top-level overview, paper summary, and quick usage.
- `technical_report/`: LaTeX sources, generated artifacts, and the PDF report.
- `zenith/src/zenith_harness/`: package source code.
- `zenith/src/zenith_harness/bundled/`: bundled prompts, provider agent definitions, and skills.
- `zenith/tests/`: pytest test suite.
- `zenith/pyproject.toml`: package metadata, dependencies, scripts, pytest, and ruff settings.

Core runtime modules include `cli.py`, `server.py`, `controller.py`, `coordinator.py`,
`acp_runner.py`, `storage.py`, and `models.py`.

## Build, Test, and Development Commands

Run commands from `zenith/` unless noted otherwise.

```bash
uv sync
```

Installs runtime and development dependencies from `pyproject.toml` and `uv.lock`.

```bash
uv run zenith --help
uv run zenith-server --help
```

Checks the installed CLI entry points.

```bash
uv run pytest
```

Runs the full test suite (hermetic only).

```bash
uv run pytest tests/test_coordinator.py
uv run pytest -k "test_name"
```

Run a single test file or a specific test by name.

```bash
uv run ruff check src tests
uv run ruff format src tests
uv run mypy src
```

Runs linting, formatting, and static type checks.

### Live / smoke tests (require external agents)

These are skipped by default and gated by env vars:

```bash
# Real ACP dispatch (serial)
ZENITH_SMOKE_REAL_ACP=claude uv run pytest tests/test_smoke_real_acp.py -s

# Real ACP dispatch (parallel)
ZENITH_SMOKE_REAL_ACP=claude uv run pytest tests/test_smoke_parallel_acp.py -s

# Z.ai / GLM smoke
ZENITH_RUN_ZAI_SMOKE=1 uv run pytest tests/test_smoke_zai_claude.py -s
```

## Coding Style & Naming Conventions

Use Python 3.11+ with 4-space indentation and type annotations for public or
cross-module interfaces. Follow the existing dataclass and Pydantic model style.
Keep modules focused around runtime responsibilities: CLI setup, MCP server
surface, controller state transitions, coordination, storage, and ACP execution.

Ruff is configured with a 100-character line length. Prefer descriptive snake_case
for functions and variables, PascalCase for classes, and uppercase names for
constants such as environment variable allowlists.

## Testing Guidelines

Tests use `pytest` with `pytest-asyncio`; async tests are enabled automatically.
Place tests in `zenith/tests/` and name files `test_*.py`. Add focused tests for
state transitions, task validation, storage behavior, CLI behavior, and ACP
boundary cases when changing those areas.

Prefer deterministic unit tests with mocks for dispatcher behavior. Use smoke
tests only when validating end-to-end ACP integration.

## Architecture

### How Zenith works

Zenith is an MCP server that turns a coding CLI (Claude Code, OpenCode, Codex, or Antigravity) into a **multi-agent orchestrator**. The CLI loads Zenith as an MCP server and gains 7 orchestrator tools. It acts as the orchestrator — deciding what to do — while sub-agents (workers, validators) run as isolated ACP processes.

```
Claude Code (orchestrator)
  └─ Zenith MCP server (7 tools)
       └─ ProjectController  →  MissionCoordinator
            └─ NodeDispatcher  →  ACP subprocess (claude-agent-acp / codex-acp / opencode acp)
                                    worker | validator | terminal-reviewer
```

### Layers

| Layer | Files | Responsibility |
|---|---|---|
| **CLI** | `cli.py` | `zenith init` (writes `.mcp.json` / `opencode.json` / `.codex/config.toml` + installs prompts/skills/agents), `zenith-server` (starts MCP) |
| **MCP server** | `server.py` | 3 server modes: `orchestrator` (7 tools), `worker` (1 tool: `end_node`), `terminal-reviewer` (1 tool: `submit_terminal_review`). Uses `fastmcp`. |
| **Controller** | `controller.py` | Routes the 7 MCP tool calls. Owns envelope construction, attention validation, task-list patch application. Stateless per-call — always reloads from disk. |
| **Coordinator** | `coordinator.py` | State-machine kernel. `step()` advances by one transition; `advance_project` loops `step()` until `attention_needed`, `terminal`, or `idle`. Dispatches work/validate nodes in parallel. |
| **Dispatcher** | `dispatcher.py` / `acp_runner.py` | Launches ACP subprocesses, streams their stdout, collects `WorkHandoff` / `ValidateHandoff` JSON results. |
| **Storage** | `storage.py` / `config.py` | Disk layout. All project state lives in `$ZENITH_HOME/projects/<pid>/`. `.zenith/` = durable record; `.zenith-runtime/` = orchestrator-only cursors. |
| **Assets** | `assets.py` | Jinja2-rendered prompts, bundled skills, and per-provider agent definitions under `bundled/`. |
| **Models** | `models.py` | Pydantic v2 schemas for `Task`, `TaskList`, `TaskListPatch`, `Decision`, `Envelope`, and all handoff types. |

### Project state machine

States: `Draft → MissionPlanning → MissionRunning ↔ AttentionNeeded → Done / Aborted`

- `start_project` → `MissionPlanning`
- `submit_plan` (with `TaskList`) → `MissionRunning`
- `advance_project` → loops `coordinator.step()` → may emit `AttentionNeeded`
- `decide_attention` → back to `MissionRunning` (or `Aborted` / next `MissionPlanning`)
- `end_mission` → `Done` (only when no runnable work remains)

### Task graph

Tasks are `work | validate | gate` with `depends_on` ids. The coordinator computes the "frontier" (runnable tasks: all deps in `cleared` or `superseded` status) and dispatches them in parallel up to `ZENITH_MAX_PARALLEL_NODES` (default 4).

### Providers

`providers.py` defines `claude`, `codex`, `antigravity`, and `opencode` as supported provider names. Each provider specifies its config format (`mcp_json`, `codex_config`, `opencode_config`, or `antigravity_config`), ACP command, skill dirs, and agent output dir. Adding a new CLI requires a new `ProviderDefinition` entry there plus bundled assets under `bundled/providers/<name>/`. OpenCode reads MCP from `opencode.json` (`mcp.zenith`). Antigravity reads MCP from `.agents/mcp_config.json`.

### Key env vars (runtime)

| Var | Default | Purpose |
|---|---|---|
| `ZENITH_HOME` | `~/.zenith` | Root for all project buckets |
| `ZENITH_MAX_PARALLEL_NODES` | `4` | Max concurrent ACP workers |
| `ZENITH_WORKER_ACP_COMMAND` | provider default | Override ACP binary for workers |
| `ZENITH_VALIDATOR_ACP_COMMAND` | falls back to worker | Override ACP binary for validators |
| `ANTHROPIC_BASE_URL` | — | Proxy for model routing (GLM/ZAI via `GLM_BASE_URL` / `ZAI_BASE_URL`) |

## Commit & Pull Request Guidelines

The current history uses short, imperative or descriptive commit subjects, often
with PR references, for example `Zenith Release v0.1 (#2)` and `update technical report`.
Keep commits scoped and use clear subjects that describe the user-visible change.

Pull requests should include a concise summary, the tests run, and any relevant
runtime or configuration impact. Link issues when applicable. For changes to
CLI behavior, MCP tools, provider configuration, or bundled prompts/skills,
include before/after notes or example commands.

## Security & Configuration Tips

Do not commit API keys or local credentials. Zenith forwards selected environment
variables to MCP subprocesses, so review changes to allowlists and provider
configuration carefully. Generated workspace files such as `.codex/`, `.claude/`,
`.agents/`, and `.mcp.json` belong to target projects, not necessarily this source
checkout.
