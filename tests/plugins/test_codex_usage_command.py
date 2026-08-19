from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "plugins" / "account_usage" / "codex" / "__init__.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("test_codex_usage_plugin", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_register_exposes_codex_usage_command():
    module = _load_module()
    seen = {}

    class FakeContext:
        def register_command(self, name, handler, description="", args_hint=""):
            seen.update(
                name=name,
                handler=handler,
                description=description,
                args_hint=args_hint,
            )

    module.register(FakeContext())

    assert seen["name"] == "codex-usage"
    assert seen["handler"] is module._handle_codex_usage
    assert "OpenAI Codex" in seen["description"]


def test_codex_usage_always_queries_openai_codex(monkeypatch):
    module = _load_module()
    calls = []

    class Snapshot:
        available = True

    def fake_fetch(provider, **kwargs):
        calls.append(provider)
        return Snapshot()

    def fake_render(snapshot, markdown=False):
        return [
            "Provider: openai-codex (Pro)",
            "Session: 85% remaining (15% used) • resets in 2h",
        ]

    monkeypatch.setattr("agent.account_usage.fetch_account_usage", fake_fetch)
    monkeypatch.setattr("agent.account_usage.render_account_usage_lines", fake_render)

    result = asyncio.run(module._handle_codex_usage(""))

    assert calls == ["openai-codex"]
    assert "openai-codex (Pro)" in result
    assert "85% remaining" in result
    assert "resets in 2h" in result


def test_codex_usage_reports_unavailable(monkeypatch):
    module = _load_module()

    monkeypatch.setattr("agent.account_usage.fetch_account_usage", lambda provider, **kwargs: None)

    result = asyncio.run(module._handle_codex_usage(""))

    assert "No OpenAI Codex usage data available" in result


def test_codex_usage_rejects_arguments():
    module = _load_module()

    result = asyncio.run(module._handle_codex_usage("unexpected"))

    assert result == "Usage: /codex-usage"
