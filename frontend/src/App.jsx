import { useEffect, useState } from "react";

import Sidebar from "./components/Sidebar";
import ResearchInput from "./components/ResearchInput";
import ResearchProgress from "./components/ResearchProgress";
import ResearchResults from "./components/ResearchResults";

import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("research");

  const [jobId, setJobId] = useState(null);
  const [job, setJob] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ---------------------------------------------------------
  // START RESEARCH
  // ---------------------------------------------------------

  const startResearch = async (goal, maxIterations, document) => {
    setLoading(true);
    setError("");
    setJob(null);
    setJobId(null);

    try {
      const formData = new FormData();
      formData.append("goal", goal);
      formData.append("max_iterations", String(maxIterations));

      if (document) {
        formData.append("document", document);
      }

      const response = await fetch(
        `${API_BASE}/api/research`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const data = await response.json().catch(() => null);

        throw new Error(
          data?.detail || "Failed to start research"
        );
      }

      const data = await response.json();

      setJobId(data.id);
      setActivePage("research");
    } catch (err) {
      setError(
        err.message || "Something went wrong"
      );
    } finally {
      setLoading(false);
    }
  };

  // ---------------------------------------------------------
  // POLL RESEARCH STATUS
  // ---------------------------------------------------------

  useEffect(() => {
    if (!jobId) return;

    let cancelled = false;
    let timer = null;

    const poll = async () => {
      try {
        const response = await fetch(
          `${API_BASE}/api/research/${jobId}`
        );

        if (!response.ok) {
          throw new Error(
            "Failed to fetch research status"
          );
        }

        const data = await response.json();

        if (!cancelled) {
          setJob(data);
        }

        if (
          data.status !== "completed" &&
          data.status !== "failed"
        ) {
          timer = setTimeout(poll, 1500);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "Unable to check research status"
          );
        }
      }
    };

    poll();

    return () => {
      cancelled = true;

      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [jobId]);

  // ---------------------------------------------------------
  // RESET RESEARCH
  // ---------------------------------------------------------

  const resetResearch = () => {
    setJobId(null);
    setJob(null);
    setError("");
    setLoading(false);
    setActivePage("research");
  };

  // ---------------------------------------------------------
  // RESEARCH PAGE
  // ---------------------------------------------------------

  const renderResearchPage = () => {
    // Initial research screen
    if (!jobId && !job) {
      return (
        <>
          <ResearchInput
            onSubmit={startResearch}
            loading={loading}
          />

          <div className="workflow-strip">
            <div className="workflow-item">
              <span>01</span>

              <div>
                <strong>Plan</strong>
                <small>
                  Break the goal into tasks
                </small>
              </div>
            </div>

            <div className="workflow-line" />

            <div className="workflow-item">
              <span>02</span>

              <div>
                <strong>Research</strong>
                <small>
                  Search and collect evidence
                </small>
              </div>
            </div>

            <div className="workflow-line" />

            <div className="workflow-item">
              <span>03</span>

              <div>
                <strong>Verify</strong>
                <small>
                  Check evidence and gaps
                </small>
              </div>
            </div>

            <div className="workflow-line" />

            <div className="workflow-item">
              <span>04</span>

              <div>
                <strong>Report</strong>
                <small>
                  Generate the final PDF
                </small>
              </div>
            </div>
          </div>
        </>
      );
    }

    // Research running
    if (
      jobId &&
      job?.status !== "completed" &&
      job?.status !== "failed"
    ) {
      return <ResearchProgress job={job} />;
    }

    // Research completed
    if (
      job?.status === "completed" &&
      job.result
    ) {
      return (
        <ResearchResults
          job={job}
          apiBase={API_BASE}
        />
      );
    }

    // Research failed
    if (job?.status === "failed") {
      return (
        <div className="failed-card">
          <div className="failed-icon">
            !
          </div>

          <div>
            <h3>Research stopped</h3>

            <p>
              {job.error ||
                "An unexpected error occurred."}
            </p>
          </div>

          <button onClick={resetResearch}>
            Try Again
          </button>
        </div>
      );
    }

    return null;
  };

  // ---------------------------------------------------------
  // PLACEHOLDER PAGES
  // ---------------------------------------------------------

  const renderPlaceholderPage = () => {
    const pages = {
      reports: {
        label: "WORKSPACE",
        title: "Reports",
        description:
          "Your completed research reports will appear here.",
        icon: "▣",
      },

      knowledge: {
        label: "WORKSPACE",
        title: "Knowledge Base",
        description:
          "Upload documents and give ResearchPilot additional knowledge.",
        icon: "◇",
      },

      workflow: {
        label: "AGENT",
        title: "Agent Workflow",
        description:
          "Visualize how ResearchPilot plans, researches, verifies and generates reports.",
        icon: "◎",
      },

      sources: {
        label: "AGENT",
        title: "Sources",
        description:
          "Sources collected during your research runs will appear here.",
        icon: "◈",
      },
    };

    const page = pages[activePage];

    if (!page) {
      return null;
    }

    return (
      <div className="placeholder-page">
        <div className="placeholder-icon">
          {page.icon}
        </div>

        <div className="section-kicker">
          {page.label}
        </div>

        <h2>{page.title}</h2>

        <p>{page.description}</p>

        <div className="placeholder-card">
          <span>Coming next</span>

          <strong>
            We're building this section.
          </strong>

          <small>
            Your existing ResearchPilot workflow
            remains untouched.
          </small>
        </div>
      </div>
    );
  };

  // ---------------------------------------------------------
  // MAIN PAGE
  // ---------------------------------------------------------

  const renderPage = () => {
    if (activePage === "research") {
      return renderResearchPage();
    }

    return renderPlaceholderPage();
  };

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div className="app-shell">

      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
      />

      <main className="main-content">

        <div className="topbar">

          <div>
            <div className="eyebrow">
              AUTONOMOUS RESEARCH
            </div>

            <h1>ResearchPilot</h1>

            <p>
              Plan, research, verify and generate
              a complete research report.
            </p>
          </div>

          {job?.status === "completed" &&
            activePage === "research" && (
              <button
                className="new-research-btn"
                onClick={resetResearch}
              >
                + New Research
              </button>
            )}
        </div>

        {error && (
          <div className="error-box">
            <strong>
              Research error
            </strong>

            <span>{error}</span>

            <button
              onClick={() => setError("")}
              className="error-close"
            >
              ×
            </button>
          </div>
        )}

        {renderPage()}

      </main>
    </div>
  );
}

export default App;