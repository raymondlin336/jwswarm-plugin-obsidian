"""Loads the tool for tests, with a stand-in for openjiuwen when WorkSwarm's package isn't installed."""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

TOOL_FILE = (
    Path(__file__).parents[1] / "obsidian-cli" / "tools" / "obsidian_cli_tool.py"
)


def _install_openjiuwen_stand_in() -> None:
    class ToolCard:
        def __init__(self, **fields):
            self.__dict__.update(fields)

    class Tool:
        def __init__(self, card):
            self.card = card

    module = types.ModuleType("openjiuwen.core.foundation.tool")
    module.Tool = Tool
    module.ToolCard = ToolCard
    for name in ("openjiuwen", "openjiuwen.core", "openjiuwen.core.foundation"):
        sys.modules.setdefault(name, types.ModuleType(name))
    sys.modules["openjiuwen.core.foundation.tool"] = module


@pytest.fixture(scope="session")
def tool_module():
    if importlib.util.find_spec("openjiuwen") is None:
        _install_openjiuwen_stand_in()
    spec = importlib.util.spec_from_file_location("obsidian_cli_tool", TOOL_FILE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
