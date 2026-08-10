from __future__ import annotations

from typing import Any

from agentic_core.contracts import Explanation
from agentic_core.settings import AgentSettings


class Narrator:
    """Produces an explanation only; policy output is never delegated to a model."""

    def __init__(self, settings: AgentSettings | None = None) -> None:
        self.settings = settings or AgentSettings()

    def explain(self, domain: str, request: str, result: dict[str, Any], evidence: list[dict[str, Any]], fallback: Explanation) -> tuple[Explanation, str]:
        if not self.settings.openai_api_key:
            return fallback, "deterministic"
        try:
            from langchain_openai import ChatOpenAI

            prompt = (
                "You are an operations copilot. Explain only the supplied deterministic result. "
                "Do not invent facts, change decisions, or suggest autonomous execution. "
                f"Domain: {domain}\nRequest: {request}\nResult: {result}\nEvidence: {evidence}"
            )
            model = ChatOpenAI(
                model=self.settings.openai_model,
                temperature=0,
                api_key=self.settings.openai_api_key,
            )
            response = model.with_structured_output(Explanation).invoke(prompt)
            return response, "openai"
        except Exception:
            return fallback, "deterministic"
