# Fraud Investigation Risk Copilot

An end-to-end, synthetic-data agentic FinTech project. The agent uses LangGraph to collect verified evidence, run a deterministic policy, generate a structured explanation through OpenAI GPT-5.6 Luna when configured, and require a human review decision.

## Architecture

- `app/domain.py`: domain tools, deterministic policy, and agent entrypoint.
- `app/main.py`: versioned API and in-memory review queue for the demo.
- `agentic_core/`: reusable LangGraph, OpenAI structured-output, persistence, and optional Langfuse primitives bundled so this repository runs independently.
- `tests/`: agent workflow acceptance test.

The LLM is never permitted to alter the deterministic result. With no API key, the complete workflow uses a deterministic explanation fallback. With `OPENAI_API_KEY` configured, the narrator uses `gpt-5.6-luna` by default.

## Run API with Docker Compose

Run credential-free by default:

```bash
docker compose up --build
```

API: `http://localhost:8103`. Health check: `GET /health`.

This API runs independently after cloning. In the complete portfolio workspace, the shared Next.js console exposes it as one of twelve tabs.

To enable GPT-5.6 Luna explanations or Langfuse tracing, copy `.env.example` to `.env` and set only the relevant variables.

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

1. `POST /api/v1/analyses` with `{"objective":"Investigate the current synthetic scenario."}`.
2. Inspect evidence, trace, deterministic result, and explanation.
3. Record a simulated reviewer decision using `POST /api/v1/analyses/{run_id}/review`.

No endpoint can move funds, file reports, block a payment, or modify production systems.
