"""Runs the tool against the real CLI. Only ever targets the test vault, and only when requested.

Run with OBSIDIAN_LIVE=1. The test vault must be registered in Obsidian as "vault3".
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("OBSIDIAN_LIVE") != "1", reason="set OBSIDIAN_LIVE=1 to run"
)

BENCHMARK = Path(__file__).parents[2] / "benchmark"
VAULT = Path.home() / "obsidian-bench" / "vault3"
VAULT_NAME = "vault3"


def _reset():
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(BENCHMARK / "reset-vault.ps1"),
        ],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def run(tool_module):
    tool = tool_module.ObsidianCliTool()

    def call(command, **inputs):
        return asyncio.run(
            tool.invoke({"command": command, "vault": VAULT_NAME, **inputs})
        )

    _reset()
    assert call("vault", options={"info": "path"})["output"] == str(VAULT)
    yield call
    # Clear any open dialog, restore the files, then reload so the app picks up the settings.
    call("reload")
    _reset()
    call("reload")


def test_reads_and_finds_tasks(run):
    assert (
        "$48,000"
        in run("read", options={"path": "Projects/Project Atlas.md"})["output"]
    )
    assert run("tasks", flags=["todo", "total"])["output"] == "7"


def test_missing_file_is_a_failure(run):
    result = run("read", options={"path": "Does Not Exist.md"})
    assert (result["success"], result["error_code"]) == (False, "command_failed")


def test_multiline_and_unicode_content_round_trips(run):
    run("create", options={"path": "Unicode Test.md", "content": "第一行\nsecond é"})
    assert (
        run("read", options={"path": "Unicode Test.md"})["output"] == "第一行\nsecond é"
    )


def test_rename_stops_with_the_setting_off(run):
    result = run("rename", options={"file": "Project Atlas", "name": "Project Apollo"})
    assert result["error_code"] == "link_updates_off"
    assert (VAULT / "Projects" / "Project Atlas.md").exists()


def test_rename_updates_links_with_the_setting_on(run):
    # Obsidian keeps settings in memory and `reload` doesn't reread app.json, so set it in the
    # app the way the settings screen does. That also saves it to app.json, where the tool looks.
    set_links = "app.vault.setConfig('alwaysUpdateLinks', {})"
    app_json = VAULT / ".obsidian" / "app.json"
    assert run("eval", options={"code": set_links.format("true")})["success"]
    try:
        # Obsidian saves settings shortly after a change, not immediately.
        for _ in range(20):
            if json.loads(app_json.read_text(encoding="utf-8")).get(
                "alwaysUpdateLinks"
            ):
                break
            time.sleep(0.5)
        else:
            pytest.fail("Obsidian didn't save the link setting to app.json")
        assert (
            run("rename", options={"file": "Project Atlas", "name": "Project Apollo"})[
                "success"
            ]
            is True
        )
        assert (
            run("backlinks", options={"file": "Project Apollo"}, flags=["total"])[
                "output"
            ]
            == "5"
        )
        assert run("unresolved", flags=["total"])["output"] == "0"
    finally:
        run("eval", options={"code": set_links.format("false")})


def test_timeout_reports_the_dialog_and_returns(run, tool_module, monkeypatch):
    monkeypatch.setattr(tool_module, "_COMMAND_TIMEOUT_SECONDS", 5)
    monkeypatch.setattr(tool_module, "_links_update_automatically", lambda *_: True)
    result = run("rename", options={"file": "Project Atlas", "name": "Project Apollo"})
    assert result["error_code"] == "timeout"
    assert "Update links" in result["error"]
