function ResearchProgress({ job }) {
  if (!job) {
    return (
      <section className="progress-card">
        <div className="progress-loading">
          Waiting for research to start...
        </div>
      </section>
    );
  }

  const stages = [
    {
      key: "planning",
      number: "01",
      title: "Planning",
      description: "Breaking the objective into research tasks",
    },
    {
      key: "researching",
      number: "02",
      title: "Researching",
      description: "Gathering information and evidence",
    },
    {
      key: "verifying",
      number: "03",
      title: "Verifying",
      description: "Checking evidence and identifying gaps",
    },
    {
      key: "reporting",
      number: "04",
      title: "Reporting",
      description: "Synthesizing the final research report",
    },
    {
      key: "complete",
      number: "05",
      title: "Complete",
      description: "Research report is ready",
    },
  ];

  const currentIndex = stages.findIndex(
    (stage) => stage.key === job.stage
  );

  return (
    <section className="research-progress">
      <div className="progress-header">
        <div>
          <span className="section-kicker">LIVE AGENT ACTIVITY</span>
          <h2>Research in progress</h2>
        </div>

        <div className="running-badge">
          <span />
          {job.status === "completed"
            ? "Complete"
            : "Agent working"}
        </div>
      </div>

      <div className="progress-track">
        {stages.map((stage, index) => {
          const active = index === currentIndex;
          const complete =
            currentIndex >= 0 && index < currentIndex;

          return (
            <div
              className={`progress-stage ${
                active ? "active" : ""
              } ${complete ? "complete" : ""}`}
              key={stage.key}
            >
              <div className="stage-number">
                {complete ? "✓" : stage.number}
              </div>

              <div className="stage-content">
                <strong>{stage.title}</strong>
                <span>{stage.description}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="activity-panel">
        <div className="activity-title">
          <span className="pulse-dot" />
          Agent activity
        </div>

        <div className="activity-list">
          {(job.activity || []).map((activity, index) => (
            <div
              className="activity-item"
              key={`${activity}-${index}`}
            >
              <span className="activity-line" />
              <span>{activity}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default ResearchProgress;