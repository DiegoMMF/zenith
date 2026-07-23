"""CLI integration tests — init / list-projects / show-project / install-skills."""
from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
import yaml
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
        r = runner.invoke(
            cli, ["init", "--workspace-dir", str(workspace), "--agent", "claude"]
        )
        assert r.exit_code == 0, r.output
        assert gitignore.read_text() == original

    def test_idempotent(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        for _ in range(2):
            r = runner.invoke(
                cli, ["init", "--workspace-dir", str(workspace), "--agent", "claude"]
            )
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

    def test_omnigent_init_writes_agent_bundle(
        self, runner: CliRunner, workspace: Path, harness_home: Path, env: dict[str, str]
    ) -> None:
        r = runner.invoke(
            cli,
            [
                "init",
                "--workspace-dir",
                str(workspace),
                "--agent",
                "omnigent",
                "--zenith-home",
                str(harness_home),
            ],
        )
        assert r.exit_code == 0, r.output

        bundle = workspace / ".omnigent" / "zenith-orchestrator"
        config_path = bundle / "config.yaml"
        agents_md = bundle / "AGENTS.md"
        assert config_path.exists()
        assert agents_md.exists()
        assert not (workspace / ".mcp.json").exists()

        payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert payload["spec_version"] == 1
        assert payload["name"] == "zenith-orchestrator"
        assert payload["instructions"] == "AGENTS.md"
        assert payload["executor"]["type"] == "omnigent"
        assert payload["executor"]["config"]["harness"] == "claude-sdk"
        assert payload["os_env"] == {
            "type": "caller_process",
            "cwd": ".",
            "sandbox": {"type": "none"},
        }
        zenith_tool = payload["tools"]["zenith"]
        assert zenith_tool["type"] == "mcp"
        assert zenith_tool["command"] == "uv"
        assert zenith_tool["args"] == _expected_mcp_server_args()
        tool_env = zenith_tool["env"]
        assert tool_env["ZENITH_ORCHESTRATOR_PROVIDER"] == "omnigent"
        assert tool_env["ZENITH_WORKER_PROVIDER"] == "claude"
        assert tool_env["ZENITH_WORKER_ACP_COMMAND"] == "claude-agent-acp"
        assert tool_env["ZENITH_HOME"] == str(harness_home.resolve())
        assert "omnigent run .omnigent/zenith-orchestrator" in r.output

    def test_omnigent_init_custom_harness_and_workers(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        r = runner.invoke(
            cli,
            [
                "init",
                "--workspace-dir",
                str(workspace),
                "--agent",
                "omnigent",
                "--omnigent-harness",
                "opencode",
                "--worker-provider",
                "opencode",
                "--worker-acp-command",
                "custom-opencode-acp",
                "--validator-provider",
                "codex",
                "--validator-acp-command",
                "custom-validator-acp",
            ],
        )
        assert r.exit_code == 0, r.output

        payload = yaml.safe_load(
            (workspace / ".omnigent" / "zenith-orchestrator" / "config.yaml").read_text(
                encoding="utf-8"
            )
        )
        assert payload["executor"]["config"]["harness"] == "opencode"
        tool_env = payload["tools"]["zenith"]["env"]
        assert tool_env["ZENITH_ORCHESTRATOR_PROVIDER"] == "omnigent"
        assert tool_env["ZENITH_WORKER_PROVIDER"] == "opencode"
        assert tool_env["ZENITH_WORKER_ACP_COMMAND"] == "custom-opencode-acp"
        assert tool_env["ZENITH_VALIDATOR_PROVIDER"] == "codex"
        assert tool_env["ZENITH_VALIDATOR_ACP_COMMAND"] == "custom-validator-acp"

    def test_omnigent_harness_rejected_for_non_omnigent_agent(
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
                "--omnigent-harness",
                "opencode",
            ],
        )
        assert r.exit_code != 0
        assert "omnigent-harness" in r.output
        assert not (workspace / ".omnigent" / "zenith-orchestrator").exists()
        assert not (workspace / ".mcp.json").exists()

    def test_omnigent_init_idempotent_preserves_prompt_and_neighbors(
        self, runner: CliRunner, workspace: Path, env: dict[str, str]
    ) -> None:
        first = runner.invoke(
            cli, ["init", "--workspace-dir", str(workspace), "--agent", "omnigent"]
        )
        assert first.exit_code == 0, first.output

        bundle = workspace / ".omnigent" / "zenith-orchestrator"
        agents_md = bundle / "AGENTS.md"
        custom_prompt = "# local orchestrator edits\n"
        agents_md.write_text(custom_prompt, encoding="utf-8")
        neighbor = bundle / "notes.txt"
        neighbor.write_text("keep me\n", encoding="utf-8")
        config_path = bundle / "config.yaml"
        config_path.write_text("name: stale\n", encoding="utf-8")

        second = runner.invoke(
            cli, ["init", "--workspace-dir", str(workspace), "--agent", "omnigent"]
        )
        assert second.exit_code == 0, second.output
        assert agents_md.read_text(encoding="utf-8") == custom_prompt
        assert neighbor.read_text(encoding="utf-8") == "keep me\n"
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert payload["name"] == "zenith-orchestrator"
        assert payload["executor"]["config"]["harness"] == "claude-sdk"

    def test_omnigent_init_forwards_only_allowed_model_env(
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

        r = runner.invoke(
            cli, ["init", "--workspace-dir", str(workspace), "--agent", "omnigent"]
        )
        assert r.exit_code == 0, r.output

        payload = yaml.safe_load(
            (workspace / ".omnigent" / "zenith-orchestrator" / "config.yaml").read_text(
                encoding="utf-8"
            )
        )
        tool_env = payload["tools"]["zenith"]["env"]
        assert tool_env["ANTHROPIC_BASE_URL"] == "https://api.z.ai/api/anthropic"
        assert tool_env["ANTHROPIC_MODEL"] == "glm-5.2[1m]"
        assert tool_env["ZAI_API_KEY"] == "zai-test-key"
        assert "DATABASE_URL" not in tool_env


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
