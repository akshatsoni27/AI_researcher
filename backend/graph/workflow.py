from langgraph.graph import StateGraph, START, END

from backend.graph.state import ResearchState

from backend.agents.planner import planner_node
from backend.agents.researcher import researcher_node
from backend.agents.verifier import verifier_node
from backend.agents.report_generator import report_generator_node


def after_research(state: ResearchState):
    """
    Decide whether more research tasks remain.
    """

    if state["pending_tasks"]:
        return "researcher"

    return "verifier"


def after_verification(state: ResearchState):
    """
    Decide whether the research is complete or
    additional research is required.
    """

    # Evidence is sufficient → generate final report
    if state["verification_status"] == "sufficient":
        return "report_generator"

    # Prevent infinite research loops
    if state["iteration"] >= state["max_iterations"]:
        return "report_generator"

    # No follow-up tasks were generated
    if not state["pending_tasks"]:
        return "report_generator"

    # Continue research
    return "researcher"


def create_research_graph():

    builder = StateGraph(ResearchState)

    # ---------------------------------------------------------
    # NODES
    # ---------------------------------------------------------

    builder.add_node(
        "planner",
        planner_node,
    )

    builder.add_node(
        "researcher",
        researcher_node,
    )

    builder.add_node(
        "verifier",
        verifier_node,
    )

    builder.add_node(
        "report_generator",
        report_generator_node,
    )

    # ---------------------------------------------------------
    # INITIAL FLOW
    # ---------------------------------------------------------

    builder.add_edge(
        START,
        "planner",
    )

    builder.add_edge(
        "planner",
        "researcher",
    )

    # ---------------------------------------------------------
    # RESEARCH LOOP
    # ---------------------------------------------------------

    builder.add_conditional_edges(
        "researcher",
        after_research,
        {
            "researcher": "researcher",
            "verifier": "verifier",
        },
    )

    # ---------------------------------------------------------
    # VERIFICATION LOOP
    # ---------------------------------------------------------

    builder.add_conditional_edges(
        "verifier",
        after_verification,
        {
            "researcher": "researcher",
            "report_generator": "report_generator",
        },
    )

    # ---------------------------------------------------------
    # FINAL REPORT
    # ---------------------------------------------------------

    builder.add_edge(
        "report_generator",
        END,
    )

    return builder.compile()