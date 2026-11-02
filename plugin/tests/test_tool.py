"""Tool behavior without Obsidian: the CLI call is replaced by a fake."""

import asyncio
import types

import pytest


@pytest.fixture
def run(tool_module):
    tool = tool_module.ObsidianCliTool()
    return lambda **inputs: asyncio.run(tool.invoke(inputs))


@pytest.fixture
def fake_cli(tool_module, monkeypatch, tmp_path):
    """Put a fake Obsidian.com in the default location and record each CLI call."""
    cli = tmp_path / "Programs" / "Obsidian" / "Obsidian.com"
    cli.parent.mkdir(parents=True)
    cli.touch()
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(tool_module.sys, "platform", "win32")
    monkeypatch.setattr(tool_module.time, "sleep", lambda _: None)

    calls = []
    results = []

    def execute(cli_path, vault, args, timeout):
        calls.append((cli_path, vault, args))
        return results.pop(0) if results else tool_module._CliResult("ok", 0)

    monkeypatch.setattr(tool_module, "_execute", execute)
    return types.SimpleNamespace(
        cli=cli, calls=calls, results=results, tmp_path=tmp_path
    )


def test_success_builds_args_in_order(run, fake_cli):
    result = run(
        command="search",
        options={"query": "North wind", "limit": 5},
        flags=["case"],
        vault="Work",
    )
    assert result == {"success": True, "command": "search", "output": "ok"}
    _, vault, args = fake_cli.calls[0]
    assert vault == "Work"
    assert args == ["search", "query=North wind", "limit=5", "case"]


def test_line_breaks_are_escaped(run, fake_cli):
    run(command="create", options={"content": "a\r\nb\tc"})
    assert fake_cli.calls[0][2][1] == "content=a\\nb\\tc"


def test_unsupported_os(run, fake_cli, tool_module, monkeypatch):
    monkeypatch.setattr(tool_module.sys, "platform", "darwin")
    assert run(command="search")["error_code"] == "unsupported_os"


def test_cli_not_found(run, fake_cli):
    fake_cli.cli.unlink()
    assert run(command="search")["error_code"] == "cli_not_found"


@pytest.mark.parametrize("name", ["bad.exe", "missing/Obsidian.com"])
def test_invalid_cli_path(run, fake_cli, name):
    (fake_cli.tmp_path / "bad.exe").touch()
    result = run(command="search", cli_path=str(fake_cli.tmp_path / name))
    assert result["error_code"] == "invalid_cli_path"
    assert fake_cli.calls == []


def test_valid_cli_path_is_used(run, fake_cli):
    custom = fake_cli.tmp_path / "Custom" / "Obsidian.com"
    custom.parent.mkdir()
    custom.touch()
    assert run(command="search", cli_path=str(custom))["success"] is True
    assert fake_cli.calls[0][0] == custom


@pytest.mark.parametrize(
    "inputs",
    [
        {},
        {"command": "two words"},
        {"command": "a", "options": []},
        {"command": "a", "options": {"vault": "x"}},
    ],
)
def test_invalid_input(run, fake_cli, inputs):
    assert run(**inputs)["error_code"] == "invalid_input"


def test_error_text_is_a_failure(run, fake_cli, tool_module):
    fake_cli.results.append(tool_module._CliResult("Error: File not found", 0))
    result = run(command="read")
    assert (result["success"], result["error_code"]) == (False, "command_failed")
    assert result["error"] == "Error: File not found"


def test_nonzero_exit_is_a_failure(run, fake_cli, tool_module):
    fake_cli.results.append(tool_module._CliResult("", 1))
    assert run(command="read")["error_code"] == "command_failed"


def test_retries_when_a_targeted_vault_is_still_loading(run, fake_cli, tool_module):
    fake_cli.results.append(
        tool_module._CliResult('Error: Command "read" not found.', 0)
    )
    assert run(command="read", vault="Work")["success"] is True
    assert len(fake_cli.calls) == 2


def test_no_retry_without_a_targeted_vault(run, fake_cli, tool_module):
    fake_cli.results.append(
        tool_module._CliResult('Error: Command "nope" not found.', 0)
    )
    assert run(command="nope")["error_code"] == "command_failed"
    assert len(fake_cli.calls) == 1


def test_timeout_reports_open_dialog(run, fake_cli, tool_module):
    fake_cli.results.extend(
        [
            tool_module._CliResult("", None, timed_out=True),
            tool_module._CliResult("Update links", 0),
        ]
    )
    result = run(command="command")
    assert result["error_code"] == "timeout"
    assert "Update links" in result["error"]


def test_timeout_without_a_dialog(run, fake_cli, tool_module):
    fake_cli.results.extend(
        [
            tool_module._CliResult("", None, timed_out=True),
            tool_module._CliResult("No elements found.", 0),
        ]
    )
    result = run(command="command")
    assert result["error_code"] == "timeout"
    assert "dialog" not in result["error"]


@pytest.mark.parametrize("command", ["rename", "move"])
@pytest.mark.parametrize(
    "settings", [None, "{}", '{"alwaysUpdateLinks": false}', "not json"]
)
def test_rename_stops_when_links_do_not_update(
    run, fake_cli, tool_module, command, settings
):
    vault = fake_cli.tmp_path / "vault"
    (vault / ".obsidian").mkdir(parents=True)
    if settings is not None:
        (vault / ".obsidian" / "app.json").write_text(settings, encoding="utf-8")
    fake_cli.results.append(tool_module._CliResult(str(vault), 0))
    assert (
        run(command=command, options={"file": "A"})["error_code"] == "link_updates_off"
    )
    assert len(fake_cli.calls) == 1


def test_rename_runs_when_links_update(run, fake_cli, tool_module):
    vault = fake_cli.tmp_path / "vault"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / ".obsidian" / "app.json").write_text(
        '{"alwaysUpdateLinks": true}', encoding="utf-8"
    )
    fake_cli.results.append(tool_module._CliResult(str(vault), 0))
    assert run(command="rename", options={"file": "A", "name": "B"})["success"] is True
    assert fake_cli.calls[1][2] == ["rename", "file=A", "name=B"]


def test_long_output_is_truncated(run, fake_cli, tool_module):
    fake_cli.results.append(
        tool_module._CliResult("x" * (tool_module._MAX_OUTPUT_CHARS + 1), 0)
    )
    result = run(command="files")
    assert result["truncated"] is True
    assert len(result["output"]) == tool_module._MAX_OUTPUT_CHARS


def test_unexpected_errors_become_failures(run, fake_cli, tool_module, monkeypatch):
    def explode(*_):
        raise OSError("boom")

    monkeypatch.setattr(tool_module, "_execute", explode)
    result = run(command="search")
    assert (result["success"], result["error_code"], result["error"]) == (
        False,
        "command_failed",
        "boom",
    )
