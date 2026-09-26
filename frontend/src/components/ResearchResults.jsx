import { useState } from "react";

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

function cleanChatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/__(.*?)__/g, "$1")
    .replace(/`([^`]+)`/g, "$1");
}

function parseTableRow(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cleanChatText(cell.trim()));
}

function renderChatContent(content) {
  const lines = content.split("\n");
  const blocks = [];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index].trim();

    if (!line) continue;

    if (line.startsWith("|") && line.includes("|")) {
      const tableRows = [];

      while (index < lines.length && lines[index].trim().startsWith("|")) {
        const tableLine = lines[index].trim();
        if (!/^\|?\s*:?-{3,}/.test(tableLine.replace(/\|/g, ""))) {
          tableRows.push(parseTableRow(tableLine));
        }
        index += 1;
      }
      index -= 1;

      if (tableRows.length) {
        blocks.push(
          <div className="chat-table-wrap" key={`table-${index}`}>
            <table className="chat-table">
              <thead>
                <tr>
                  {tableRows[0].map((cell, cellIndex) => (
                    <th key={cellIndex}>{cell}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableRows.slice(1).map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      continue;
    }

    if (line.startsWith("### ") || line.startsWith("## ")) {
      blocks.push(
        <h4 key={index}>{cleanChatText(line.replace(/^###? /, ""))}</h4>
      );
      continue;
    }

    if (/^[-*] /.test(line) || /^\d+\. /.test(line)) {
      blocks.push(
        <div className="chat-list-item" key={index}>
          {cleanChatText(line.replace(/^([-*] |\d+\. )/, ""))}
        </div>
      );
      continue;
    }

    blocks.push(<p key={index}>{cleanChatText(line)}</p>);
  }

  return blocks;
}

function ResearchResults({ job, apiBase }) {
  const result = job.result || {};
  const parsedReport = result.final_report
    ? parseReport(result.final_report)
    : null;
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");
  const [chatMinimized, setChatMinimized] = useState(false);

  const downloadPdf = () => {
    window.open(
      `${apiBase}/api/research/${job.id}/pdf`,
      "_blank"
    );
  };

  const askFollowUp = async (event) => {
    event.preventDefault();

    const question = chatQuestion.trim();
    if (!question || chatLoading) return;

    setChatLoading(true);
    setChatError("");
    setChatMessages((messages) => [
      ...messages,
      { role: "user", content: question },
    ]);
    setChatQuestion("");

    try {
      const response = await fetch(
        `${apiBase}/api/research/${job.id}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question }),
        }
      );
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail || "The follow-up answer could not be generated."
        );
      }

      setChatMessages((messages) => [
        ...messages,
        { role: "assistant", content: data.answer },
      ]);
    } catch (error) {
      setChatError(error.message || "Unable to send the follow-up question.");
    } finally {
      setChatLoading(false);
    }
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

      <section className={`research-chat${chatMinimized ? " minimized" : ""}`}>
        <div className="sources-header">
          <div>
            <span className="section-kicker">FOLLOW-UP</span>
            <h2>Ask about this research</h2>
          </div>
          <div className="chat-header-actions">
            {!chatMinimized && (
              <span className="source-count">Research + web search</span>
            )}
            <button
              className="chat-minimize-button"
              type="button"
              onClick={() => setChatMinimized((current) => !current)}
              aria-label={chatMinimized ? "Open follow-up chat" : "Minimize follow-up chat"}
              title={chatMinimized ? "Open chat" : "Minimize chat"}
            >
              {chatMinimized ? "+" : "−"}
            </button>
          </div>
        </div>

        {!chatMinimized && chatMessages.length > 0 && (
          <div className="chat-messages" aria-live="polite">
            {chatMessages.map((message, index) => (
              <div className={`chat-message ${message.role}`} key={index}>
                <span>{message.role === "user" ? "YOU" : "RESEARCHPILOT"}</span>
                <div className="chat-content">
                  {renderChatContent(message.content)}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="chat-message assistant">
                <span>RESEARCHPILOT</span>
                <div className="chat-content">
                  <p>Searching and reasoning over the research...</p>
                </div>
              </div>
            )}
          </div>
        )}

        {!chatMinimized && chatError && <p className="chat-error">{chatError}</p>}

        {!chatMinimized && <form className="chat-form" onSubmit={askFollowUp}>
          <textarea
            value={chatQuestion}
            onChange={(event) => setChatQuestion(event.target.value)}
            placeholder="Ask a follow-up question about the findings..."
            maxLength={2000}
            rows={3}
            disabled={chatLoading}
          />
          <button type="submit" disabled={!chatQuestion.trim() || chatLoading}>
            {chatLoading ? "Answering..." : "Ask follow-up"}
          </button>
        </form>}
      </section>
    </section>
  );
}

export default ResearchResults;