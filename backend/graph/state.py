from typing import TypedDict


class ResearchState(TypedDict):
    user_goal: str

    research_plan: list[str]

    current_task: str
    completed_tasks: list[str]
    pending_tasks: list[str]

    queries: list[str]

    sources: list[dict]
    evidence: list[dict]

    research_gaps: list[str]

    research_mode: str
    document_context: bool

    verification_status: str
    verification_notes: list[str]

    iteration: int
    max_iterations: int

    final_report: str