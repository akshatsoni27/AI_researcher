import SourceList from "./SourceList";

const REPORT_SECTIONS = [
  "Executive Summary",
  "Key Findings",
  "Detailed Analysis",
  "Evidence and Sources",
  "Limitations",
  "Conclusion",
];

function parseReport(report) {
  const sections = Object.fromEntries(
    REPORT_SECTIONS.map((heading) => [heading, []])
  );
  let title = "Research Report";
  let activeSection = null;

  report.split("\n").forEach((line) => {
    const trimmed = line.trim();

    if (trimmed.startsWith("# ")) {
      title = trimmed.slice(2).trim();
      return;
    }

    if (trimmed.startsWith("## ")) {
      const heading = trimmed.slice(3).trim();
      activeSection = REPORT_SECTIONS.find(
        (section) => section.toLowerCase() === heading.toLowerCase()
      );
      return;
    }

    if (activeSection) {
      sections[activeSection].push(line);
    }
  });

  return { title, sections };
}

function renderSectionLine(line, index) {
  const trimmed = line.trim();

  if (!trimmed) {
    return <br key={index} />;
  }

  if (trimmed.startsWith("### ")) {
    return <h3 key={index}>{trimmed.slice(4)}</h3>;
  }

  if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
    return <li key={index}>{trimmed.slice(2)}</li>;
  }

  if (/^\d+\. /.test(trimmed)) {
    return <li key={index}>{trimmed.replace(/^\d+\. /, "")}</li>;
  }

  return <p key={index}>{trimmed}</p>;
}

function ResearchResults({ job, apiBase }) {
  const result = job.result || {};
  const parsedReport = result.final_report
    ? parseReport(result.final_report)
    : null;

  const downloadPdf = () => {
    window.open(
      `${apiBase}/api/research/${job.id}/pdf`,
      "_blank"
    );
  };

  return (
    <section className="results-section">
      <div className="results-header">
        <div>
          <span className="section-kicker">
            RESEARCH OUTPUT
          </span>

          <h2>Research report</h2>

          <p>
            Evidence collected and verified by ResearchPilot.
          </p>
        </div>

        <button
          className="download-button"
          onClick={downloadPdf}
        >
          <span>↓</span>
          Download PDF
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>RESEARCH TASKS</span>
          <strong>
            {result.completed_tasks?.length || 0}
          </strong>
        </div>

        <div className="stat-card">
          <span>EVIDENCE</span>
          <strong>
            {result.evidence?.length || 0}
          </strong>
        </div>

        <div className="stat-card">
          <span>WEB SOURCES</span>
          <strong>
            {result.evidence?.filter(
              (item) => item.source_type === "web"
            ).length || 0}
          </strong>
        </div>

        <div className="stat-card">
          <span>DOCUMENT SOURCES</span>
          <strong>
            {result.evidence?.filter(
              (item) => item.source_type === "document"
            ).length || 0}
          </strong>
        </div>
      </div>

      <div className="report-layout">
        <div className="report-main">
          <div className="report-card">
            <div className="report-card-header">
              <span>FINAL REPORT</span>

              <div className="verification-status">
                <span />
                {result.verification_status ||
                  "verified"}
              </div>
            </div>

            <article className="report-content">
              {parsedReport ? (
                <>
                  <h1>{parsedReport.title}</h1>

                  {REPORT_SECTIONS.map((heading) => {
                    const lines = parsedReport.sections[heading];

                    if (!lines.some((line) => line.trim())) {
                      return null;
                    }

                    return (
                      <section className="report-section" key={heading}>
                        <h2>{heading}</h2>
                        <div>
                          {lines.map((line, index) =>
                            renderSectionLine(line, index)
                          )}
                        </div>
                      </section>
                    );
                  })}
                </>
              ) : (
                <p>No report content available.</p>
              )}
            </article>
          </div>
        </div>

        <aside className="results-sidebar">
          <div className="side-card">
            <div className="side-card-title">
              Research goal
            </div>

            <p>{result.user_goal}</p>
          </div>

          {result.research_gaps?.length > 0 && (
            <div className="side-card">
              <div className="side-card-title">
                Research gaps
              </div>

              <ul>
                {result.research_gaps.map((gap, index) => (
                  <li key={index}>{gap}</li>
                ))}
              </ul>
            </div>
          )}
        </aside>
      </div>

      <div className="sources-section">
        <div className="sources-header">
          <div>
            <span className="section-kicker">
              EVIDENCE
            </span>
            <h2>Sources collected</h2>
          </div>

          <span className="source-count">
            {result.evidence?.length || 0} sources
          </span>
        </div>

        <SourceList evidence={result.evidence} />
      </div>
    </section>
  );
}

export default ResearchResults;