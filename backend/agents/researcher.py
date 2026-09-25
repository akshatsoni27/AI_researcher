from typing import Literal

from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

from backend.tools.web_search import web_search
from backend.rag.retriever import search_knowledge_base


# ---------------------------------------------------------
# RESEARCH ROUTING
# ---------------------------------------------------------


class ResearchDecision(BaseModel):
    mode: Literal["web", "document", "hybrid"] = Field(
        description=(
            "Choose whether to use web search, "
            "document RAG, or both."
        )
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)


decision_llm = llm.with_structured_output(
    ResearchDecision,
    method="json_mode",
)


def decide_research_mode(
    task: str,
    document_available: bool,
) -> str:
    """
    Decide which research source should be used.

    web:
        Current or external information.

    document:
        Information that should come from the
        uploaded knowledge base.

    hybrid:
        Both document evidence and current web
        information are required.
    """

    prompt = f"""
You are the research routing component of an
autonomous research agent.

Research task:
{task}

A document knowledge base is available:
{document_available}

Choose exactly one research mode.

Available modes:

web
Use live web research when the task requires
current, external, or publicly available information.

document
Use the uploaded document knowledge base when
the task should be answered from the provided documents.

hybrid
Use BOTH the uploaded documents and live web research
when the task requires comparing document information
with current external information.

Rules:

1. If no document knowledge base is available,
   you MUST choose web.

2. Never choose document or hybrid when no document
   knowledge base is available.

3. Use hybrid when the task contains concepts such as:
   compare, contrast, validate, verify against,
   update the document, latest developments relative
   to the document, or similar language.

4. Use web when the task asks about:
   latest information, current developments,
   recent releases, trends, news, or 2026 information.

5. Use document when the task explicitly asks about
   the uploaded material itself.

Return JSON containing the selected mode.

The mode must be exactly one of:

web
document
hybrid

IMPORTANT:
Return JSON.
"""

    try:

        decision = decision_llm.invoke(prompt)

        return decision.mode

    except Exception as error:

        print(
            f"\n[Routing Warning] "
            f"Research routing failed: {error}"
        )

        # Safe fallback
        if document_available:
            return "hybrid"

        return "web"


# ---------------------------------------------------------
# RESEARCHER NODE
# ---------------------------------------------------------


def researcher_node(state: dict):
    """
    Execute the next research task.

    The researcher can:

    1. Search the web
    2. Search the document knowledge base
    3. Use both
    4. Continue even when one source fails
    5. Avoid duplicate web sources
    """

    pending_tasks = list(
        state.get("pending_tasks", [])
    )

    # -----------------------------------------------------
    # NO TASKS LEFT
    # -----------------------------------------------------

    if not pending_tasks:

        return {
            "current_task": "",
        }

    # -----------------------------------------------------
    # SELECT CURRENT TASK
    # -----------------------------------------------------

    current_task = pending_tasks[0]

    document_available = state.get(
        "document_context",
        False,
    )

    # -----------------------------------------------------
    # DECIDE RESEARCH MODE
    # -----------------------------------------------------

    mode = decide_research_mode(
        current_task,
        document_available,
    )

    print(
        f"\n[Researcher] Task: {current_task}"
    )

    print(
        f"[Researcher] Mode: {mode}"
    )

    # -----------------------------------------------------
    # COPY EXISTING STATE
    # -----------------------------------------------------

    sources = list(
        state.get("sources", [])
    )

    evidence = list(
        state.get("evidence", [])
    )

    queries = list(
        state.get("queries", [])
    )

    completed_tasks = list(
        state.get("completed_tasks", [])
    )

    # -----------------------------------------------------
    # WEB RESEARCH
    # -----------------------------------------------------

    if mode in ("web", "hybrid"):

        print(
            "[Researcher] Searching the web..."
        )

        try:

            web_results = web_search(
                current_task,
                max_results=5,
            )

        except Exception as error:

            print(
                f"\n[Web Research Warning] "
                f"Search failed: {error}"
            )

            web_results = []

        # Record query
        if current_task not in queries:
            queries.append(current_task)

        # -------------------------------------------------
        # WEB SEARCH FAILED
        # -------------------------------------------------

        if not web_results:

            print(
                "[Researcher] No usable web results found."
            )

            evidence.append(
                {
                    "task": current_task,
                    "source_type": "web",
                    "title": "Web search failed",
                    "url": "",
                    "content": (
                        "No usable web results were found "
                        "for this research task."
                    ),
                }
            )

        # -------------------------------------------------
        # PROCESS WEB RESULTS
        # -------------------------------------------------

        else:

            print(
                f"[Researcher] "
                f"Found {len(web_results)} web results."
            )

            existing_urls = {
                source.get("url")
                for source in sources
                if source.get("type") == "web"
                and source.get("url")
            }

            for result in web_results:

                title = result.get(
                    "title",
                    "",
                ).strip()

                url = result.get(
                    "url",
                    "",
                ).strip()

                snippet = result.get(
                    "snippet",
                    "",
                ).strip()

                # Ignore incomplete results
                if not title or not url:
                    continue

                # -------------------------------------------------
                # SOURCE DEDUPLICATION
                # -------------------------------------------------

                if url not in existing_urls:

                    sources.append(
                        {
                            "type": "web",
                            "title": title,
                            "url": url,
                        }
                    )

                    existing_urls.add(url)

                # -------------------------------------------------
                # EVIDENCE
                # -------------------------------------------------

                evidence.append(
                    {
                        "task": current_task,
                        "source_type": "web",
                        "title": title,
                        "url": url,
                        "content": snippet,
                    }
                )

    # -----------------------------------------------------
    # DOCUMENT / RAG RESEARCH
    # -----------------------------------------------------

    if mode in ("document", "hybrid"):

        print(
            "[Researcher] Searching document knowledge base..."
        )

        if not document_available:

            print(
                "[RAG Warning] "
                "No document knowledge base is available."
            )

            evidence.append(
                {
                    "task": current_task,
                    "source_type": "document",
                    "source": "Knowledge base",
                    "page": "",
                    "content": (
                        "Document research was requested, "
                        "but no knowledge base is available."
                    ),
                }
            )

        else:

            try:

                document_results = search_knowledge_base(
                    current_task,
                    k=5,
                )

            except Exception as error:

                print(
                    f"\n[RAG Warning] "
                    f"Document search failed: {error}"
                )

                document_results = []

            # -------------------------------------------------
            # NO DOCUMENT RESULTS
            # -------------------------------------------------

            if not document_results:

                print(
                    "[Researcher] "
                    "No relevant document evidence found."
                )

                evidence.append(
                    {
                        "task": current_task,
                        "source_type": "document",
                        "source": "Knowledge base",
                        "page": "",
                        "content": (
                            "No relevant document evidence "
                            "was found for this research task."
                        ),
                    }
                )

            # -------------------------------------------------
            # PROCESS DOCUMENT RESULTS
            # -------------------------------------------------

            else:

                print(
                    f"[Researcher] "
                    f"Found {len(document_results)} "
                    f"document results."
                )

                for result in document_results:

                    source = result.get(
                        "source",
                        "Unknown document",
                    )

                    page = result.get(
                        "page",
                        "",
                    )

                    content = result.get(
                        "content",
                        "",
                    )

                    sources.append(
                        {
                            "type": "document",
                            "source": source,
                            "page": page,
                        }
                    )

                    evidence.append(
                        {
                            "task": current_task,
                            "source_type": "document",
                            "source": source,
                            "page": page,
                            "content": content,
                        }
                    )

    # -----------------------------------------------------
    # MARK TASK COMPLETE
    # -----------------------------------------------------

    completed_tasks.append(
        current_task
    )

    # Remove the current task
    remaining_tasks = pending_tasks[1:]

    print(
        "[Researcher] Task completed."
    )

    print(
        f"[Researcher] "
        f"Remaining tasks: {len(remaining_tasks)}"
    )

    # -----------------------------------------------------
    # RETURN UPDATED STATE
    # -----------------------------------------------------

    return {
        "current_task": current_task,

        "research_mode": mode,

        "pending_tasks": remaining_tasks,

        "completed_tasks": completed_tasks,

        "queries": queries,

        "sources": sources,

        "evidence": evidence,

        # Do not change the verification iteration here.
        "iteration": state.get(
            "iteration",
            0,
        ),
    }