"""CLI integration tests — init / list-projects / show-project / install-skills."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
from click.testing import CliRunner

from zenith_harness.cli import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def env(harness_home: Path, workspace: Path, monkeypatch) -> dict[str, str]:
    monkeypatch.setenv("ZENITH_HOME", str(harness_home))
    monkeypatch.chdir(workspace)
    return {"ZENITH_HOME": str(harness_home)}


def _expected_mcp_server_args() -> list[str]:
    zenith_root = Path(__file__).resolve().parents[1]
    return [
        "run",
        "--project",
        str(zenith_root),
        "zenith-server",
        "--mode",
        "orchestrator",
    ]


class TestInit:
    def test_stages_host_agent_surface_only(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        """`zenith init` writes MCP config + provider agents + orchestrator prompt
        but does NOT create the project bucket or workspace shims — those are
        created by `start_project` at the first MCP call."""
        result = runner.invoke(
            cli, ["init", "--workspace-dir", str(workspace), "--agent", "claude"]
        )
        assert result.exit_code == 0, result.output
        # Workspace stays clean of .zenith/ — bucket lives under ZENITH_HOME.
        assert not (workspace / ".zenith").exists()
        # No symlink shims either — start_project handles them.
        assert not (workspace / "AGENTS.md").exists()
        # MCP config + .claude/agents/ are written.
        assert (workspace / ".mcp.json").exists()
        mcp = json.loads((workspace / ".mcp.json").read_text())
        assert "zenith" in mcp["mcpServers"]
        server = mcp["mcpServers"]["zenith"]
        assert server["command"] == "uv"
        assert server["args"] == _expected_mcp_server_args()

    def test_init_does_not_touch_gitignore(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        gitignore = workspace / ".gitignore"
        gitignore.write_text("node_modules/\n")
        original = gitignore.read_text()
        r = runner.invoke(cli, ["init", "--workspace-dir", str(workspace), "--agent", "claude"])
        assert r.exit_code == 0, r.output
        assert gitignore.read_text() == original

    def test_idempotent(self, runner: CliRunner, workspace: Path, env: dict[str, str]) -> None:
        for _ in range(2):
            r = runner.invoke(cli, ["init", "--workspace-dir", str(workspace), "--agent", "claude"])
            assert r.exit_code == 0, r.output
        # .mcp.json preserved across reruns.
        assert (workspace / ".mcp.json").exists()

    def test_codex_writes_codex_config(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        r = runner.invoke(cli, ["init", "--workspace-dir", str(workspace), "--agent", "codex"])
        assert r.exit_code == 0, r.output
        config_path = workspace / ".codex" / "config.toml"
        assert config_path.exists()
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
        server = config["mcp_servers"]["zenith"]
        assert server["command"] == "uv"
        assert server["args"] == _expected_mcp_server_args()
        assert f"Initialized v5 project workspace at {workspace}" in r.output
        assert "Start your agent from the initialized project workspace" in r.output
        assert (
            "First read .codex/orchestrator_prompt.md and treat it as your primary role, "
            "then use Zenith to run this mission." in r.output
        )

    def test_opencode_writes_opencode_json(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        for _ in range(2):
            r = runner.invoke(
                cli, ["init", "--workspace-dir", str(workspace), "--agent", "opencode"]
            )
            assert r.exit_code == 0, r.output

        opencode_path = workspace / "opencode.json"
        assert opencode_path.exists()
        opencode = json.loads(opencode_path.read_text(encoding="utf-8"))
        assert opencode["$schema"] == "https://opencode.ai/config.json"
        server = opencode["mcp"]["zenith"]
        assert server["type"] == "local"
        assert server["command"] == ["uv", *_expected_mcp_server_args()]
        assert server["enabled"] is True
        assert server["timeout"] == 60000
        assert server["environment"]["ZENITH_ORCHESTRATOR_PROVIDER"] == "opencode"
        assert server["environment"]["ZENITH_WORKER_PROVIDER"] == "opencode"
        assert server["environment"]["ZENITH_WORKER_ACP_COMMAND"] == "opencode acp"

        # Compatibility: still write Claude-style .mcp.json (OpenCode ignores it).
        mcp = json.loads((workspace / ".mcp.json").read_text(encoding="utf-8"))
        assert mcp["mcpServers"]["zenith"]["command"] == "uv"
        assert mcp["mcpServers"]["zenith"]["args"] == _expected_mcp_server_args()

        assert (workspace / ".opencode" / "orchestrator_prompt.md").exists()
        assert (
            "First read .opencode/orchestrator_prompt.md and treat it as your primary role, "
            "then use Zenith to run this mission." in r.output
        )

    def test_opencode_preserves_existing_opencode_json(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        opencode_path = workspace / "opencode.json"
        opencode_path.write_text(
            json.dumps(
                {
                    "$schema": "https://opencode.ai/config.json",
                    "model": "opencode/gpt-5",
                    "mcp": {
                        "other": {
                            "type": "remote",
                            "url": "https://example.com/mcp",
                        }
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        r = runner.invoke(cli, ["init", "--workspace-dir", str(workspace), "--agent", "opencode"])
        assert r.exit_code == 0, r.output
        opencode = json.loads(opencode_path.read_text(encoding="utf-8"))
        assert opencode["model"] == "opencode/gpt-5"
        assert opencode["mcp"]["other"]["url"] == "https://example.com/mcp"
        assert opencode["mcp"]["zenith"]["type"] == "local"

    def test_antigravity_writes_agents_mcp_config(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        for _ in range(2):
            r = runner.invoke(
                cli, ["init", "--workspace-dir", str(workspace), "--agent", "antigravity"]
            )
            assert r.exit_code == 0, r.output

        mcp_path = workspace / ".agents" / "mcp_config.json"
        assert mcp_path.exists()
        mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        server = mcp["mcpServers"]["zenith"]
        assert server["command"] == "uv"
        assert server["args"] == _expected_mcp_server_args()
        assert server["env"]["ZENITH_ORCHESTRATOR_PROVIDER"] == "antigravity"
        assert server["env"]["ZENITH_WORKER_PROVIDER"] == "antigravity"
        assert server["env"]["ZENITH_WORKER_ACP_COMMAND"] == "python -m agy_acp_server"
        assert not (workspace / ".mcp.json").exists()
        assert (workspace / ".antigravity" / "orchestrator_prompt.md").exists()
        assert (
            "First read .antigravity/orchestrator_prompt.md and treat it as your primary role, "
            "then use Zenith to run this mission." in r.output
        )

    def test_antigravity_preserves_existing_agents_mcp_config(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        mcp_path = workspace / ".agents" / "mcp_config.json"
        mcp_path.parent.mkdir(parents=True, exist_ok=True)
        mcp_path.write_text(
            json.dumps(
                {
                    "mcpServers": {
                        "other": {
                            "command": "other-mcp",
                            "args": [],
                        }
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        r = runner.invoke(
            cli, ["init", "--workspace-dir", str(workspace), "--agent", "antigravity"]
        )
        assert r.exit_code == 0, r.output
        mcp = json.loads(mcp_path.read_text(encoding="utf-8"))
        assert mcp["mcpServers"]["other"]["command"] == "other-mcp"
        assert mcp["mcpServers"]["zenith"]["command"] == "uv"
        assert mcp["mcpServers"]["zenith"]["args"] == _expected_mcp_server_args()

    def test_claude_init_writes_runtime_validator_env_names(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        r = runner.invoke(
            cli,
            [
                "init",
                "--workspace-dir",
                str(workspace),
                "--agent",
                "claude",
                "--validator-provider",
                "codex",
                "--validator-acp-command",
                "custom-validator-acp",
            ],
        )
        assert r.exit_code == 0, r.output

        mcp = json.loads((workspace / ".mcp.json").read_text())
        mcp_env = mcp["mcpServers"]["zenith"]["env"]
        assert mcp_env["ZENITH_VALIDATOR_PROVIDER"] == "codex"
        assert mcp_env["ZENITH_VALIDATOR_ACP_COMMAND"] == "custom-validator-acp"
        assert "ZENITH_VALIDATION_WORKER_PROVIDER" not in mcp_env
        assert "ZENITH_VALIDATION_WORKER_ACP_COMMAND" not in mcp_env

    def test_claude_init_forwards_only_allowed_model_env(
        self,
        runner: CliRunner,
        workspace: Path,
        env: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")
        monkeypatch.setenv("ANTHROPIC_MODEL", "glm-5.2[1m]")
        monkeypatch.setenv("ZAI_API_KEY", "zai-test-key")
        monkeypatch.setenv("DATABASE_URL", "postgres://should-not-forward")

        r = runner.invoke(cli, ["init", "--workspace-dir", str(workspace), "--agent", "claude"])
        assert r.exit_code == 0, r.output

        mcp = json.loads((workspace / ".mcp.json").read_text())
        mcp_env = mcp["mcpServers"]["zenith"]["env"]
        assert mcp_env["ANTHROPIC_BASE_URL"] == "https://api.z.ai/api/anthropic"
        assert mcp_env["ANTHROPIC_MODEL"] == "glm-5.2[1m]"
        assert mcp_env["ZAI_API_KEY"] == "zai-test-key"
        assert "DATABASE_URL" not in mcp_env


class TestListProjects:
    def test_empty(self, runner: CliRunner, env: dict[str, str]) -> None:
        r = runner.invoke(cli, ["list-projects"])
        assert r.exit_code == 0
        assert "No projects" in r.output

    def test_after_creation(
        self, runner: CliRunner, workspace: Path, harness_home: Path, env: dict[str, str]
    ) -> None:
        from zenith_harness.config import HarnessConfig
        from zenith_harness.storage import ProjectStore

        ProjectStore(HarnessConfig.discover()).create_project(
            "brief", workspace, project_id="proj-x"
        )
        r = runner.invoke(cli, ["list-projects"])
        assert "proj-x" in r.output


class TestShowProject:
    def test_unknown_id(self, runner: CliRunner, env: dict[str, str]) -> None:
        r = runner.invoke(cli, ["show-project", "ghost"])
        assert r.exit_code != 0
        assert "not found" in r.output.lower()
