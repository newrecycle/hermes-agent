"""Built-in OpenAI Codex / ChatGPT subscription usage command."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


async def _handle_codex_usage(raw_args: str) -> str:
    """Return Codex subscription limits independently of the active model provider."""
    if (raw_args or "").strip():
        return "Usage: /codex-usage"

    def _fetch_and_render() -> str:
        from agent.account_usage import fetch_account_usage, render_account_usage_lines

        snapshot = fetch_account_usage("openai-codex")
        if not snapshot or not snapshot.available:
            return (
                "No OpenAI Codex usage data available. "
                "Make sure you're signed in with the OpenAI Codex / ChatGPT account first."
            )
        return "\n".join(render_account_usage_lines(snapshot))

    try:
        return await asyncio.to_thread(_fetch_and_render)
    except Exception as exc:
        logger.warning("Codex usage lookup failed: %s", exc, exc_info=True)
        return f"OpenAI Codex usage lookup failed: {exc}"


def register(ctx) -> None:
    """Register /codex-usage on CLI, TUI, and gateway surfaces."""
    ctx.register_command(
        "codex-usage",
        _handle_codex_usage,
        description="Show OpenAI Codex / ChatGPT subscription usage and reset time",
    )
