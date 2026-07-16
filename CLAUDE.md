# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `zenith/` (the Python package root):

```bash
cd zenith
uv sync                        # install deps + dev deps
uv run zenith --help           # CLI entrypoint
uv run zenith-server --help    # MCP server entrypoint
uv run pytest                  # full test suite (hermetic only)
uv run pytest tests/test_coordinator.py  # single test file
uv run pytest -k "test_name"   # single test by name
uv run ruff check src/ tests/  # lint
uv run ruff format src/ tests/ # format
uv run mypy src/               # type check
```

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

## Architecture

### How Zenith works

Zenith is an MCP server that turns a coding CLI (Claude Code or Codex) into a **multi-agent orchestrator**. The CLI loads Zenith as an MCP server and gains 7 orchestrator tools. It acts as the orchestrator — deciding what to do — while sub-agents (workers, validators) run as isolated ACP processes.

```
Claude Code (orchestrator)
  └─ Zenith MCP server (7 tools)
       └─ ProjectController  →  MissionCoordinator
            └─ NodeDispatcher  →  ACP subprocess (claude-agent-acp / codex-acp)
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

`providers.py` defines `claude`, `codex`, `antigravity`, and `opencode` as supported provider names. Each provider specifies its config format (`mcp_json`, `codex_config`, or `opencode_config`), ACP command, skill dirs, and agent output dir. Adding a new CLI requires a new `ProviderDefinition` entry there plus bundled assets under `bundled/providers/<name>/`. OpenCode reads MCP from `opencode.json` (`mcp.zenith`); `.mcp.json` is still written for harness compatibility but OpenCode ignores it.

### Key env vars (runtime)

| Var | Default | Purpose |
|---|---|---|
| `ZENITH_HOME` | `~/.zenith` | Root for all project buckets |
| `ZENITH_MAX_PARALLEL_NODES` | `4` | Max concurrent ACP workers |
| `ZENITH_WORKER_ACP_COMMAND` | provider default | Override ACP binary for workers |
| `ZENITH_VALIDATOR_ACP_COMMAND` | falls back to worker | Override ACP binary for validators |
| `ANTHROPIC_BASE_URL` | — | Proxy for model routing (GLM/ZAI via `GLM_BASE_URL` / `ZAI_BASE_URL`) |
