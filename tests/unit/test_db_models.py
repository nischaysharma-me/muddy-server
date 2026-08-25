"""Unit tests for SQLAlchemy 2.0 Async Models and Database Transactions."""

import uuid
import pytest
from sqlalchemy import select
from app.db import (
    AgentSessionModel,
    JobModel,
    PipelineLogModel,
    ToolLogModel,
    async_session_factory,
    init_db,
)


@pytest.mark.asyncio
async def test_init_db_and_job_crud():
    # Initialize DB schema
    await init_db()

    async with async_session_factory() as session:
        async with session.begin():
            test_job_id = str(uuid.uuid4())
            job = JobModel(
                id=test_job_id,
                status="queued",
                progress=0.0,
                job_type="article_generation",
                payload={"topic": "Distributed Systems"},
            )
            session.add(job)

        # Query in new transaction
        async with session.begin():
            stmt = select(JobModel).where(JobModel.id == test_job_id)
            result = await session.scalar(stmt)
            assert result is not None
            assert result.status == "queued"
            assert result.payload["topic"] == "Distributed Systems"

            # Update progress
            result.progress = 50.0
            result.status = "processing"


@pytest.mark.asyncio
async def test_agent_session_and_audit_logs():
    async with async_session_factory() as session:
        async with session.begin():
            sess_id = f"session-{uuid.uuid4()}"
            agent_sess = AgentSessionModel(
                session_id=sess_id,
                agent_type="conversational",
                provider="openrouter",
                model="anthropic/claude-3.5-sonnet",
                state_snapshot={"history_length": 5},
            )
            session.add(agent_sess)

            # Add Tool Log
            tool_log = ToolLogModel(
                session_id=sess_id,
                tool_name="web_search",
                arguments={"query": "LangGraph"},
                result={"status": "ok"},
                duration_ms=45.2,
            )
            session.add(tool_log)

            # Add Pipeline Log
            pipe_log = PipelineLogModel(
                pipeline_name="article_pipeline",
                step_name="draft_step",
                status="SUCCESS",
                duration_ms=120.0,
            )
            session.add(pipe_log)

        # Verify insertion
        async with session.begin():
            sess_stmt = select(AgentSessionModel).where(AgentSessionModel.session_id == sess_id)
            res_sess = await session.scalar(sess_stmt)
            assert res_sess is not None
            assert res_sess.model == "anthropic/claude-3.5-sonnet"

            tool_stmt = select(ToolLogModel).where(ToolLogModel.session_id == sess_id)
            res_tool = await session.scalar(tool_stmt)
            assert res_tool is not None
            assert res_tool.tool_name == "web_search"


@pytest.mark.asyncio
async def test_transaction_rollback():
    job_id = str(uuid.uuid4())

    try:
        async with async_session_factory() as session:
            async with session.begin():
                job = JobModel(
                    id=job_id,
                    status="failed_test",
                )
                session.add(job)
                # Force failure to trigger rollback
                raise ValueError("Simulated transaction failure")
    except ValueError:
        pass

    # Verify record was rolled back and does not exist
    async with async_session_factory() as session:
        stmt = select(JobModel).where(JobModel.id == job_id)
        result = await session.scalar(stmt)
        assert result is None
