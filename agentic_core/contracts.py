from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    source: str
    fact: str
    value: Any


class Explanation(BaseModel):
    summary: str
    rationale: str
    next_steps: list[str] = Field(min_length=1, max_length=3)


class AgentRun(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    domain: str
    request: str
    status: Literal["pending_review", "approved", "rejected"] = "pending_review"
    deterministic_result: dict[str, Any]
    evidence: list[Evidence]
    explanation: Explanation
    trace: list[str]
    model_mode: Literal["deterministic", "openai"]
    reviewer_note: str | None = None


class ReviewCommand(BaseModel):
    decision: Literal["approved", "rejected"]
    note: str = Field(min_length=3, max_length=500)
