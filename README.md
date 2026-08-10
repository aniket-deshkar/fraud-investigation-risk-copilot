# Fraud Investigation Risk Copilot

## Problem Statement

Fraud analysts receive high volumes of alerts and must correlate transaction values, customer behaviour, device signals, and counterparty relationships before deciding which cases deserve attention.

## Solution

The service computes reproducible risk signals, applies explicit thresholds, builds a prioritized review queue, and uses GPT-5.6 Luna to summarize only the verified evidence. LangGraph records every investigation step and a human reviewer records the final case decision.

## How It Works

1. Domain tools collect verified evidence from the project fixtures.
2. Deterministic policy code calculates the domain result.
3. LangGraph records evidence collection, policy evaluation, structured explanation, and human review as explicit workflow stages.
4. OpenAI GPT-5.6 Luna produces a typed explanation from the recorded result and evidence.
5. SQLAlchemy persists the run, trace, evidence, explanation, and reviewer decision in SQLite.

## Architecture

- `app/domain.py`: domain tools, deterministic policy, and agent entrypoint.
- `app/main.py`: FastAPI endpoints, CORS policy, persistence, health reporting, and review commands.
- `agentic_core/`: reusable LangGraph orchestration, OpenAI structured output, SQLAlchemy persistence, contracts, configuration, and Langfuse tracing.
- `tests/`: workflow, API lifecycle, persistence, review, and OpenAI integration tests.
- `docs/`: high-level design, low-level design, and technical design proposal.

The deterministic result remains the system of record. The model converts supplied evidence and computed results into a typed operational explanation.

## Technology Stack

Python 3.12+, FastAPI, Pydantic, LangGraph, LangChain OpenAI, OpenAI GPT-5.6 Luna, SQLAlchemy, SQLite, Langfuse, Docker, and Docker Compose.

## Configuration

Copy `.env.example` to `.env` and provide the desired integrations:

```dotenv
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-5.6-luna
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
```

Environment files are excluded from version control.

## Run with Docker Compose

```bash
docker compose up --build
```

API: `http://localhost:8103`. Health check: `GET /health`.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
python -m unittest discover -s tests -v
```

## API Workflow

1. `POST /api/v1/analyses` with `{"objective":"Investigate the supplied portfolio scenario."}`.
2. Inspect evidence, trace, deterministic result, and explanation.
3. Retrieve the persisted run with `GET /api/v1/analyses/{run_id}`.
4. Record the reviewer decision with `POST /api/v1/analyses/{run_id}/review`.
