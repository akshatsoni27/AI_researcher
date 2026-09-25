import { useState } from "react";

function SourceList({ evidence = [] }) {
  const [showAll, setShowAll] = useState(false);

  if (!evidence.length) {
    return (
      <div className="empty-sources">
        No sources were collected.
      </div>
    );
  }

  const visibleEvidence = showAll ? evidence : evidence.slice(0, 4);

  return (
    <>
      <div className="source-list">
        {visibleEvidence.map((item, index) => (
        <div
          className="source-card"
          key={`${item.url || item.source}-${index}`}
        >
          <div className="source-number">
            {String(index + 1).padStart(2, "0")}
          </div>

          <div className="source-content">
            <div className="source-type">
              {item.source_type === "web"
                ? "WEB SOURCE"
                : "DOCUMENT"}
            </div>

            <h4>
              {item.source_type === "web"
                ? item.title
                : item.source}
            </h4>

            {item.source_type === "web" ? (
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
              >
                {item.url}
              </a>
            ) : (
              <span className="document-page">
                Page {item.page}
              </span>
            )}

            {item.content && (
              <p>{item.content.slice(0, 280)}...</p>
            )}
          </div>
        </div>
        ))}
      </div>

      {evidence.length > 4 && (
        <button
          className="source-toggle"
          type="button"
          onClick={() => setShowAll((current) => !current)}
          aria-expanded={showAll}
        >
          {showAll ? "Show fewer sources" : `Show more sources (${evidence.length - 4})`}
        </button>
      )}
    </>
  );
}

export default SourceList;