from langchain_groq import ChatGroq


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


MAX_EVIDENCE_CHARS = 18000
MAX_CONTENT_PER_SOURCE = 1500


def report_generator_node(state: dict):
    """
    Generate a concise research report from the verified evidence.
    """

    goal = state["user_goal"]
    evidence = state.get("evidence", [])

    if not evidence:
        return {
            "final_report": (
                "No sufficient evidence was collected to generate "
                "a research report."
            )
        }

    evidence_blocks = []

    for index, item in enumerate(evidence, start=1):

        if item.get("source_type") == "web":

            source_info = (
                f"Source type: Web\n"
                f"Title: {item.get('title', 'Unknown')}\n"
                f"URL: {item.get('url', 'Unknown')}"
            )

        else:

            source_info = (
                f"Source type: Document\n"
                f"Source: {item.get('source', 'Unknown')}\n"
                f"Page: {item.get('page', 'Unknown')}"
            )

        content = item.get("content", "")

        evidence_blocks.append(
            f"""
SOURCE {index}
{source_info}

Evidence:
{content[:MAX_CONTENT_PER_SOURCE]}
"""
        )

    combined_evidence = "\n".join(evidence_blocks)

    combined_evidence = combined_evidence[:MAX_EVIDENCE_CHARS]

    prompt = f"""
You are the final report generator for an autonomous research system.

Research goal:
{goal}

Verified research evidence:
{combined_evidence}

Create a clear, factual research report answering the research goal.

Requirements:

1. Start with a short executive summary.
2. Organize the report using meaningful headings.
3. Synthesize information instead of simply listing sources.
4. Clearly distinguish facts from uncertainty.
5. Do not invent information.
6. Only make claims supported by the provided evidence.
7. When evidence comes from a web source, include its URL.
8. When evidence comes from a document, include the document
   name and page number.
9. Mention important research limitations or gaps.
10. Keep the report concise but useful.

Use this structure:

# Research Report

## Executive Summary

## Key Findings

## Detailed Analysis

## Evidence and Sources

## Limitations

## Conclusion

Return only the final report.
"""

    response = llm.invoke(prompt)

    return {
        "final_report": response.content
    }