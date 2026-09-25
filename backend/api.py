from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.graph.workflow import create_research_graph
from backend.reports.pdf_generator import generate_pdf_report


app = FastAPI(
    title="ResearchPilot API",
    version="0.1.0",
    description="API adapter for the existing ResearchPilot LangGraph workflow.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_jobs: dict[str, dict[str, Any]] = {}
_jobs_lock = Lock()


class ResearchRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=1000)
    max_iterations: int = Field(default=2, ge=1, le=5)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _public_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": job["id"],
        "status": job["status"],
        "stage": job["stage"],
        "activity": job["activity"],
        "started_at": job["started_at"],
        "updated_at": job["updated_at"],
        "result": job.get("result"),
        "error": job.get("error"),
    }


def _set_job(job_id: str, **updates: Any) -> None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is not None:
            job.update(updates)
            job["updated_at"] = _now()


def _initial_state(request: ResearchRequest) -> dict[str, Any]:
    return {
        "user_goal": request.goal,
        "research_plan": [],
        "current_task": "",
        "completed_tasks": [],
        "pending_tasks": [],
        "queries": [],
        "sources": [],
        "evidence": [],
        "research_gaps": [],
        "research_mode": "",
        "document_context": Path("chroma_db").exists(),
        "verification_status": "",
        "verification_notes": [],
        "iteration": 0,
        "max_iterations": request.max_iterations,
        "final_report": "",
    }


def _run_research(job_id: str, request: ResearchRequest) -> None:
    try:
        graph = create_research_graph()
        state = _initial_state(request)
        _set_job(
            job_id,
            status="running",
            stage="planning",
            activity=["Research brief received", "Planning the investigation"],
        )

        for update in graph.stream(state, stream_mode="updates"):
            if not update:
                continue

            node_name = next(iter(update))
            node_state = update[node_name]
            state.update(node_state)

            stage_labels = {
                "planner": ("planning", "Plan assembled from the research goal"),
                "researcher": ("researching", "Gathering evidence and source material"),
                "verifier": ("verifying", "Checking evidence coverage and research gaps"),
                "report_generator": ("reporting", "Synthesizing the final research report"),
            }
            stage, message = stage_labels.get(
                node_name,
                ("researching", f"Agent step completed: {node_name}"),
            )
            activity = list(_jobs[job_id].get("activity", []))
            activity.append(message)
            _set_job(
                job_id,
                stage=stage,
                activity=activity[-8:],
            )

        _set_job(
            job_id,
            status="completed",
            stage="complete",
            activity=list(_jobs[job_id].get("activity", []))[-8:]
            + ["Research report ready"],
            result=state,
        )
    except Exception as error:
        _set_job(
            job_id,
            status="failed",
            stage="error",
            error=str(error),
            activity=list(_jobs.get(job_id, {}).get("activity", []))
            + ["The research run stopped unexpectedly"],
        )


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "document_context": Path("chroma_db").exists(),
    }


@app.post("/api/research")
def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    job_id = uuid4().hex
    job = {
        "id": job_id,
        "status": "queued",
        "stage": "queued",
        "activity": ["Queued for the ResearchPilot agent"],
        "started_at": _now(),
        "updated_at": _now(),
    }
    with _jobs_lock:
        _jobs[job_id] = job
    background_tasks.add_task(_run_research, job_id, request)
    return {"id": job_id}


@app.get("/api/research/{job_id}")
def get_research(job_id: str) -> dict[str, Any]:
    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Research run not found")
    return _public_job(job)


@app.get("/api/research/{job_id}/pdf")
def download_pdf(job_id: str) -> FileResponse:
    with _jobs_lock:
        job = _jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Research run not found")

    result = job.get("result") or {}
    report = result.get("final_report", "")
    if not report:
        raise HTTPException(status_code=409, detail="The report is not ready")

    filename = f"researchpilot-{job_id}.pdf"
    path = generate_pdf_report(report, filename=filename)
    return FileResponse(
        path,
        media_type="application/pdf",
        filename="researchpilot-report.pdf",
    )
