from pydantic import BaseModel, Field
from langchain_groq import ChatGroq


class VerificationResult(BaseModel):
    sufficient: bool = Field(
        description="Whether the available evidence is sufficient."
    )

    gaps: list[str] = Field(
        description="Important unanswered questions."
    )

    notes: list[str] = Field(
        description="Why evidence is or is not sufficient."
    )

    follow_up_tasks: list[str] = Field(
        description=(
            "Specific research tasks that can resolve the identified gaps. "
            "Each task should be directly executable by the researcher."
        )
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

verifier_llm = llm.with_structured_output(
    VerificationResult,
    method="json_mode",
)


MAX_EVIDENCE_CHARS = 12000
MAX_CONTENT_CHARS_PER_ITEM = 2000


def verifier_node(state: dict):
    """
    Examine collected evidence and determine whether the
    research is sufficient.

    If important gaps remain, generate concrete follow-up
    research tasks for the researcher.
    """

    evidence = state.get("evidence", [])
    goal = state["user_goal"]

    # ---------------------------------------------------------
    # NO EVIDENCE
    # ---------------------------------------------------------

    if not evidence:
        return {
            "verification_status": "insufficient",
            "research_gaps": [
                "No evidence has been collected."
            ],
            "verification_notes": [
                "The research cannot be completed without evidence."
            ],
            "pending_tasks": [
                f"Find reliable sources that directly address: {goal}"
            ],
            "iteration": state.get("iteration", 0) + 1,
        }

    # ---------------------------------------------------------
    # PREPARE EVIDENCE
    # ---------------------------------------------------------

    evidence_text = []

    for index, item in enumerate(
        evidence,
        start=1,
    ):

        if item.get("source_type") == "web":

            source = (
                f"WEB SOURCE: {item.get('title', '')}\n"
                f"URL: {item.get('url', '')}"
            )

        else:

            source = (
                f"DOCUMENT SOURCE: {item.get('source', '')}\n"
                f"PAGE: {item.get('page', '')}"
            )

        content = item.get(
            "content",
            "",
        )

        evidence_text.append(
            f"""
Evidence {index}

{source}

Content:
{content[:MAX_CONTENT_CHARS_PER_ITEM]}
"""
        )

    combined_evidence = "\n".join(
        evidence_text
    )[:MAX_EVIDENCE_CHARS]

    # ---------------------------------------------------------
    # VERIFICATION PROMPT
    # ---------------------------------------------------------

    prompt = f"""
You are the verification component of an autonomous
research agent.

Your job is NOT to write the final answer.

You MUST return the verification result as valid JSON.

Your job is to determine whether the collected evidence
is sufficient to answer the user's research goal accurately.

Research goal:
{goal}

Collected evidence:
{combined_evidence}

Evaluate the evidence carefully.

Check for:

1. Important unanswered questions
2. Claims without supporting evidence
3. Missing information required by the user's goal
4. Contradictions between sources
5. Missing recent/current information
6. Missing document evidence when relevant
7. Weak or low-quality sources
8. Missing quantitative evidence when the question requires it

IMPORTANT:

- Do not invent facts.
- Do not assume that a search result snippet proves a claim.
- Do not mark research sufficient merely because many sources exist.
- Focus on whether the evidence actually answers the user's question.
- If important information is missing, mark the research insufficient.
- Follow-up tasks must be concrete and directly researchable.

For example, instead of:

"Need more information about benchmarks"

use:

"Find recent benchmark results comparing AI coding agents on
software engineering tasks and report the benchmark name,
evaluation metric, date, and reported results."

Return the result as valid JSON matching this structure:

{{
    "sufficient": true,
    "gaps": [],
    "notes": [
        "Evidence sufficiently covers the research goal."
    ],
    "follow_up_tasks": []
}}

    The response MUST be valid JSON.
    Do not include markdown.
    Do not include explanations outside the JSON.
"""

    result = verifier_llm.invoke(prompt)

    # ---------------------------------------------------------
    # NORMALIZE RESULT
    # ---------------------------------------------------------

    status = (
        "sufficient"
        if result.sufficient
        else "insufficient"
    )

    follow_up_tasks = result.follow_up_tasks or []

    gaps = result.gaps or []

    notes = result.notes or []

    # ---------------------------------------------------------
    # RETURN UPDATED STATE
    # ---------------------------------------------------------

    return {
        "verification_status": status,

        "research_gaps": gaps,

        "verification_notes": notes,

        "pending_tasks": follow_up_tasks,

        "iteration": state.get(
            "iteration",
            0,
        ) + 1,
    }