from __future__ import annotations

from typing import Any, Callable, TypedDict

from langgraph.graph import END, START, StateGraph

from agentic_core.contracts import AgentRun, Evidence, Explanation
from agentic_core.narration import Narrator


class WorkflowState(TypedDict, total=False):
    request: str
    evidence: list[dict[str, Any]]
    result: dict[str, Any]
    explanation: Explanation
    trace: list[str]
    model_mode: str


def run_agent_workflow(
    *,
    domain: str,
    request: str,
    collect_evidence: Callable[[], list[dict[str, Any]]],
    apply_policy: Callable[[list[dict[str, Any]]], dict[str, Any]],
    fallback_explanation: Callable[[dict[str, Any]], Explanation],
    narrator: Narrator | None = None,
) -> AgentRun:
    narrator = narrator or Narrator()

    def collect(_: WorkflowState) -> WorkflowState:
        return {"evidence": collect_evidence(), "trace": ["collect_evidence"]}

    def decide(state: WorkflowState) -> WorkflowState:
        return {"result": apply_policy(state["evidence"]), "trace": state["trace"] + ["apply_deterministic_policy"]}

    def explain(state: WorkflowState) -> WorkflowState:
        explanation, model_mode = narrator.explain(domain, request, state["result"], state["evidence"], fallback_explanation(state["result"]))
        return {"explanation": explanation, "model_mode": model_mode, "trace": state["trace"] + ["produce_structured_explanation"]}

    def review_gate(state: WorkflowState) -> WorkflowState:
        return {"trace": state["trace"] + ["require_human_review"]}

    graph = StateGraph(WorkflowState)
    graph.add_node("collect", collect)
    graph.add_node("decide", decide)
    graph.add_node("explain", explain)
    graph.add_node("review_gate", review_gate)
    graph.add_edge(START, "collect")
    graph.add_edge("collect", "decide")
    graph.add_edge("decide", "explain")
    graph.add_edge("explain", "review_gate")
    graph.add_edge("review_gate", END)
    state = graph.compile().invoke({"request": request})
    return AgentRun(
        domain=domain,
        request=request,
        deterministic_result=state["result"],
        evidence=[Evidence.model_validate(item) for item in state["evidence"]],
        explanation=state["explanation"],
        trace=state["trace"],
        model_mode=state["model_mode"],
    )
