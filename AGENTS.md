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

Runs the full test suite.

```bash
uv run ruff check src tests
uv run mypy src
```

Runs linting and static type checks.

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
