from pathlib import Path

from backend.graph.workflow import create_research_graph
from backend.reports.pdf_generator import generate_pdf_report


def main():

    graph = create_research_graph()

    # ---------------------------------------------------------
    # USER INPUT
    # ---------------------------------------------------------

    goal = input(
        "\nWhat would you like to research?\n> "
    )

    document_available = Path("chroma_db").exists()

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("RESEARCH PILOT")
    print("=" * 60)

    print("\nGoal:")
    print(goal)

    if document_available:
        print("\n📄 Document knowledge base: Available")
    else:
        print("\n🌐 Research mode: Web only")

    print("\nStarting autonomous research...")

    # ---------------------------------------------------------
    # INITIAL STATE
    # ---------------------------------------------------------

    initial_state = {
        "user_goal": goal,

        "research_plan": [],

        "current_task": "",
        "completed_tasks": [],
        "pending_tasks": [],

        "queries": [],

        "sources": [],
        "evidence": [],

        "research_gaps": [],

        "research_mode": "",
        "document_context": document_available,

        "verification_status": "",
        "verification_notes": [],

        "iteration": 0,
        "max_iterations": 2,

        "final_report": "",
    }

    # ---------------------------------------------------------
    # START RESEARCH
    # ---------------------------------------------------------

    print("\n[1] Planning research...")

    result = graph.invoke(initial_state)

    # ---------------------------------------------------------
    # RESEARCH SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("RESEARCH COMPLETE")
    print("=" * 60)

    print("\nResearch goal:")
    print(result["user_goal"])

    print("\nResearch tasks completed:")
    print(len(result["completed_tasks"]))

    print("\nEvidence collected:")
    print(len(result["evidence"]))

    # ---------------------------------------------------------
    # SOURCE COUNTS
    # ---------------------------------------------------------

    web_sources = sum(
        1
        for item in result["evidence"]
        if item.get("source_type") == "web"
    )

    document_sources = sum(
        1
        for item in result["evidence"]
        if item.get("source_type") == "document"
    )

    print(f"\n🌐 Web sources: {web_sources}")
    print(f"📄 Document sources: {document_sources}")

    # ---------------------------------------------------------
    # VERIFICATION
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    print(
        f"\nStatus: {result['verification_status']}"
    )

    if result["verification_notes"]:

        print("\nVerifier notes:")

        for note in result["verification_notes"]:
            print(f"- {note}")

    if result["research_gaps"]:

        print("\nRemaining research gaps:")

        for gap in result["research_gaps"]:
            print(f"- {gap}")

    # ---------------------------------------------------------
    # FINAL REPORT
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL RESEARCH REPORT")
    print("=" * 60)

    final_report = result.get(
        "final_report",
        "",
    )

    if final_report:

        print()
        print(final_report)

    else:

        print("\nNo final report was generated.")

    # ---------------------------------------------------------
    # GENERATE PDF
    # ---------------------------------------------------------

    if final_report:

        print("\n" + "=" * 60)
        print("GENERATING PDF REPORT")
        print("=" * 60)

        try:

            pdf_path = generate_pdf_report(
                final_report,
                filename="research_report.pdf",
            )

            print("\n✓ PDF REPORT GENERATED")
            print(f"📄 Location: {pdf_path}")

        except Exception as error:

            print("\n⚠ PDF generation failed:")
            print(error)

    # ---------------------------------------------------------
    # FINAL STATUS
    # ---------------------------------------------------------

    print("\n" + "=" * 60)

    if final_report:
        print("✓ RESEARCH REPORT GENERATED")
    else:
        print("⚠ RESEARCH COMPLETED WITHOUT REPORT")

    print("=" * 60)

    print("\nResearchPilot finished processing your request.")


if __name__ == "__main__":
    main()