from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from agentic_core.settings import AgentSettings


@contextmanager
def observe_agent(name: str, payload: dict) -> Iterator[None]:
    """Exports a Langfuse observation only when the optional credentials exist."""
    settings = AgentSettings()
    if not (settings.langfuse_public_key and settings.langfuse_secret_key):
        yield
        return
    try:
        from langfuse import get_client

        client = get_client()
    except Exception:
        yield
        return
    with client.start_as_current_observation(as_type="agent", name=name, input=payload):
        yield
    try:
        client.flush()
    except Exception:
        pass
