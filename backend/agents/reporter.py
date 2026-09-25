from pydantic import BaseModel, Field
from langchain_groq import ChatGroq


class ResearchReport(BaseModel):
    title: str = Field(
        description="A clear title for the research report."
    )

    executive_summary: str = Field(
        description="A concise summary of the most important findings."
    )

    key_findings: list[str] = Field(
        description="The most important findings supported by the evidence."
    )

    detailed_analysis: str = Field(
        description="A detailed synthesis of the collected evidence."
    )

    limitations: list[str] = Field(
        description="Important limitations, uncertainties, or missing evidence."
    )

    sources: list[str] = Field(
        description="The most relevant source titles and URLs."
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

report_llm = llm.with_structured_output(
    ResearchReport,
    method="json_mode",
)


MAX_EVIDENCE_CHARS = 16000
MAX_CONTENT_PER_SOURCE = 1800


def reporter_node(state: dict):

    goal = state["user_goal"]
    evidence = state.get("evidence", [])

    if not evidence:
        return {
            "final_report": "No research evidence was collected."
        }

    evidence_blocks = []

    for index, item in enumerate(evidence, start=1):

        if item["source_type"] == "web":

            source_info = (
                f"WEB SOURCE\n"
                f"Title: {item.get('title', '')}\n"
                f"URL: {item.get('url', '')}"
            )

        else:

            source_info = (
                f"DOCUMENT SOURCE\n"
                f"Source: {item.get('source', '')}\n"
                f"Page: {item.get('page', '')}"
            )

        evidence_blocks.append(
            f"""
Evidence {index}

{source_info}

Research task:
{item.get('task', '')}

Content:
{item.get('content', '')[:MAX_CONTENT_PER_SOURCE]}
"""
        )

    evidence_text = "\n".join(evidence_blocks)
    evidence_text = evidence_text[:MAX_EVIDENCE_CHARS]

    prompt = f"""
You are the final report generation component of an
autonomous research agent.

Research goal:
{goal}

The research system collected the following evidence:

{evidence_text}

Create a reliable research report based ONLY on the
provided evidence.

Important rules:

1. Do not invent facts.
2. Do not introduce unsupported claims.
3. Clearly distinguish evidence from interpretation.
4. If evidence is incomplete, mention the limitation.
5. Prefer concrete findings over generic statements.
6. Preserve source URLs when available.
7. Do not claim that something is "latest" unless the
   collected evidence actually supports that claim.
8. If sources disagree, explicitly mention the disagreement.

Return JSON.

The JSON must contain:

{{
    "title": "Research report title",
    "executive_summary": "Short summary",
    "key_findings": [
        "Finding 1",
        "Finding 2"
    ],
    "detailed_analysis": "Detailed synthesis",
    "limitations": [
        "Important limitation"
    ],
    "sources": [
        "Source title - URL"
    ]
}}

The report should be useful to a human reader and should
directly answer the original research goal.
"""

    result = report_llm.invoke(prompt)

    report = f"""
# {result.title}

## Executive Summary

{result.executive_summary}

## Key Findings

"""

    for index, finding in enumerate(
        result.key_findings,
        start=1,
    ):
        report += f"{index}. {finding}\n"

    report += f"""

## Detailed Analysis

{result.detailed_analysis}

## Limitations

"""

    for limitation in result.limitations:
        report += f"- {limitation}\n"

    report += """

## Sources

"""

    for source in result.sources:
        report += f"- {source}\n"

    return {
        "final_report": report
    }