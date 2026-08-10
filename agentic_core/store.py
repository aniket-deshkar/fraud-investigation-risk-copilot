from __future__ import annotations

from pathlib import Path

from sqlalchemy import String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from agentic_core.contracts import AgentRun, ReviewCommand


class Base(DeclarativeBase):
    pass


class StoredRun(Base):
    __tablename__ = "agent_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class AgentRunStore:
    """Small SQLite persistence layer for synthetic portfolio run history."""

    def __init__(self, database_path: Path) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self.database_path = database_path
        self.engine = create_engine(f"sqlite:///{database_path.as_posix()}")
        Base.metadata.create_all(self.engine)

    def save(self, run: AgentRun) -> AgentRun:
        with Session(self.engine) as session:
            stored = session.get(StoredRun, run.run_id)
            if stored:
                stored.payload = run.model_dump_json()
            else:
                session.add(StoredRun(run_id=run.run_id, payload=run.model_dump_json()))
            session.commit()
        return run

    def get(self, run_id: str) -> AgentRun | None:
        with Session(self.engine) as session:
            stored = session.scalar(select(StoredRun).where(StoredRun.run_id == run_id))
            return AgentRun.model_validate_json(stored.payload) if stored else None

    def review(self, run_id: str, command: ReviewCommand) -> AgentRun | None:
        run = self.get(run_id)
        if not run:
            return None
        run.status = command.decision
        run.reviewer_note = command.note
        return self.save(run)
