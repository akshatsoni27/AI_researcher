import { useState } from "react";

function ResearchInput({ onSubmit, loading }) {
  const [goal, setGoal] = useState("");
  const [iterations, setIterations] = useState(2);
  const [document, setDocument] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!goal.trim() || loading) return;

    onSubmit(goal.trim(), Number(iterations), document);
  };

  const examples = [
    "What are the latest developments in AI coding agents in 2026?",
    "What are the major challenges of deploying AI agents in production?",
    "Compare RAG and long-context approaches for enterprise AI.",
  ];

  const useExample = (example) => {
    setGoal(example);
  };

  return (
    <section className="research-hero">
      <div className="hero-badge">
        <span />
        AUTONOMOUS RESEARCH
      </div>

      <h2>
        Give your research
        <br />
        <span>an objective.</span>
      </h2>

      <p className="hero-description">
        ResearchPilot turns a question into a structured investigation,
        gathers evidence from available sources, verifies the findings,
        and produces a research report.
      </p>

      <form
        className="research-form"
        onSubmit={handleSubmit}
      >
        <div className="input-header">
          <span>Research objective</span>

          <span className="input-hint">
            {goal.length}/1000
          </span>
        </div>

        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="What would you like ResearchPilot to investigate?"
          maxLength={1000}
          rows={5}
          disabled={loading}
        />

        <label className="document-upload">
          <span className="document-upload-copy">
            <strong>Optional PDF context</strong>
            <small>
              Upload a document to include it in the research.
            </small>
          </span>

          <span className="document-upload-action">
            {document ? document.name : "Choose PDF"}
          </span>

          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) =>
              setDocument(event.target.files?.[0] || null)
            }
            disabled={loading}
          />
        </label>

        <div className="form-footer">
          <div className="iteration-control">
            <label>Iterations</label>

            <select
              value={iterations}
              onChange={(e) => setIterations(e.target.value)}
              disabled={loading}
            >
              <option value={1}>1 iteration</option>
              <option value={2}>2 iterations</option>
              <option value={3}>3 iterations</option>
              <option value={4}>4 iterations</option>
              <option value={5}>5 iterations</option>
            </select>
          </div>

          <button
            type="submit"
            className="research-button"
            disabled={!goal.trim() || loading}
          >
            {loading ? (
              <>
                <span className="button-spinner" />
                Starting...
              </>
            ) : (
              <>
                Start Research
                <span>→</span>
              </>
            )}
          </button>
        </div>
      </form>

      <div className="examples">
        <span>Try an example</span>

        <div className="example-list">
          {examples.map((example) => (
            <button
              key={example}
              onClick={() => useExample(example)}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

export default ResearchInput;