function Sidebar({ activePage, onNavigate }) {
  const workspaceItems = [
    { id: "research", icon: "⌕", label: "Research" },
    { id: "reports", icon: "◫", label: "Reports" },
    { id: "knowledge", icon: "◈", label: "Knowledge Base" },
  ];

  const agentItems = [
    { id: "workflow", icon: "◎", label: "Workflow" },
    { id: "sources", icon: "◇", label: "Sources" },
  ];

  const renderItem = (item) => (
    <button
      key={item.id}
      className={`nav-item ${activePage === item.id ? "active" : ""}`}
      onClick={() => onNavigate(item.id)}
    >
      <span className="nav-icon">{item.icon}</span>
      <span>{item.label}</span>
    </button>
  );

  return (
    <aside className="sidebar">
      {/* BRAND */}
      <div className="brand">
        <div className="brand-logo">
          <img
            src="/mimir-logo.png"
            alt="MIMIR logo"
          />
        </div>

        <div className="brand-text">
          <strong>MIMIR</strong>
          <span>AI Research Agent</span>
        </div>
      </div>

      <div className="brand-divider" />

      {/* NAVIGATION */}
      <nav className="sidebar-nav">
        <div className="nav-section">
          <span className="nav-label">WORKSPACE</span>

          {workspaceItems.map(renderItem)}
        </div>

        <div className="nav-divider" />

        <div className="nav-section">
          <span className="nav-label">AGENT</span>

          {agentItems.map(renderItem)}
        </div>
      </nav>

      {/* BOTTOM */}
      <div className="sidebar-bottom">
        <div className="agent-status">
          <span className="status-dot" />

          <div className="agent-status-text">
            <strong>Agent Online</strong>
            <small>LangGraph workflow</small>
          </div>
        </div>

        <div className="sidebar-footer">
          MIMIR v0.1.0
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;