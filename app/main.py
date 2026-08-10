from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agentic_core.contracts import AgentRun, ReviewCommand
from agentic_core.settings import AgentSettings
from agentic_core.store import AgentRunStore
from app.domain import analyze

app = FastAPI(title="Fraud Investigation Risk Copilot", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
store = AgentRunStore(Path("data/agent_runs.db"))


class AnalysisRequest(BaseModel):
    objective: str = Field(default="Investigate the current synthetic scenario.", min_length=10, max_length=500)


@app.get("/health")
def health() -> dict[str, str | bool]:
    settings = AgentSettings()
    return {
        "status": "ok",
        "service": "fraud-investigation-risk-copilot",
        "openai_model": settings.openai_model,
        "openai_configured": bool(settings.openai_api_key),
    }


@app.post("/api/v1/analyses", response_model=AgentRun)
def create_analysis(request: AnalysisRequest) -> AgentRun:
    run = analyze(request.objective)
    return store.save(run)


@app.get("/api/v1/analyses/{run_id}", response_model=AgentRun)
def get_analysis(run_id: str) -> AgentRun:
    run = store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return run


@app.post("/api/v1/analyses/{run_id}/review", response_model=AgentRun)
def review_analysis(run_id: str, command: ReviewCommand) -> AgentRun:
    run = store.review(run_id, command)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    return run
