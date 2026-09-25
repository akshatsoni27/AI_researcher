from pydantic import BaseModel, Field
from langchain_groq import ChatGroq


class ResearchPlan(BaseModel):
    mode: str = Field(
        description="Research mode: web, document, or hybrid"
    )

    tasks: list[str] = Field(
        description="Ordered research tasks"
    )

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

planner_llm = llm.with_structured_output(
    ResearchPlan,
    method="json_mode",
)


def planner_node(state: dict):
    goal = state["user_goal"]

    prompt = f"""
You are the planning component of an autonomous research agent.

User research goal:
{state["user_goal"]}

A document knowledge base may be available.

Choose exactly ONE research mode:

WEB:
Use this when the user asks about current, general, external,
or up-to-date information and does not ask about an uploaded document.

DOCUMENT:
Use this when the user explicitly asks about the uploaded document,
PDF, or information contained inside their document.

HYBRID:
Use this when the user wants to compare, combine, validate, or
connect information from the uploaded document with external/current
information.

Important:
Do not choose DOCUMENT or HYBRID merely because a document exists.
Choose them only when the user's goal actually requires document evidence.

Create a logical sequence of research tasks.

Return valid JSON matching this structure:

{{
    "mode": "web",
    "tasks": [
        "Research task 1",
        "Research task 2",
        "Research task 3"
    ]
}}

The mode must be exactly one of:
"web", "document", "hybrid".
"""

    result = planner_llm.invoke(prompt)

    return {
    "research_plan": result.tasks,
    "pending_tasks": result.tasks.copy(),
    "research_mode": result.mode,
}