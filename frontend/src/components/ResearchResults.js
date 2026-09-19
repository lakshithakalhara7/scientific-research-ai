import "./ResearchResults.css";

function ResearchResults({
  data,
  query,
}) {
  if (!data) {
    return null;
  }

  const papers =
    data.papers || [];

  const findings =
    data.keyFindings || [];

  return (
    <section className="research-results">

      {/* HEADER */}

      <div className="results-heading">

        <div>
          <span>
            AI RESEARCH
          </span>

          <h2>
            Research Analysis
          </h2>
        </div>

        <div className="ai-status">
          <span></span>

          ANALYSIS COMPLETE
        </div>

      </div>

      {/* AGENTS */}

      <div className="agent-grid">

        <div className="agent-card">

          <div className="agent-icon">
            🔎
          </div>

          <div>
            <strong>
              Retrieval Agent
            </strong>

            <p>
              Scientific literature retrieved
            </p>
          </div>

          <span className="agent-ready">
            READY
          </span>

        </div>

        <div className="agent-card">

          <div className="agent-icon">
            ✦
          </div>

          <div>
            <strong>
              Analysis Agent
            </strong>

            <p>
              Research insights generated
            </p>
          </div>

          <span className="agent-ready">
            READY
          </span>

        </div>

        <div className="agent-card">

          <div className="agent-icon">
            ✓
          </div>

          <div>
            <strong>
              Verification Agent
            </strong>

            <p>
              Evidence verification performed
            </p>
          </div>

          <span className="agent-ready">
            VERIFIED
          </span>

        </div>

      </div>

      {/* QUESTION */}

      <div className="query-result-card">

        <div className="query-result-icon">
          ✦
        </div>

        <div>

          <span className="query-label">
            RESEARCH REQUEST
          </span>

          <h3>
            {data.question ||
              query ||
              "Research analysis"}
          </h3>

        </div>

      </div>

      {/* ANALYSIS */}

      <div className="analysis-result-card">

        <div className="analysis-result-header">

          <div className="analysis-title">

            <div className="analysis-icon">
              ✦
            </div>

            <div>
              <span>
                RESOMIND ANALYSIS
              </span>

              <h3>
                AI Research Summary
              </h3>
            </div>

          </div>

          <div className="analysis-generated">
            AI GENERATED
          </div>

        </div>

        <p className="analysis-summary">
          {data.summary}
        </p>

        {findings.length > 0 && (

          <div className="key-findings">

            <h4>
              Key Findings
            </h4>

            {findings.map(
              (finding, index) => (

                <div
                  className="finding-item"
                  key={index}
                >

                  <span>
                    {index + 1}
                  </span>

                  <p>
                    {finding}
                  </p>

                </div>

              )
            )}

          </div>

        )}

      </div>

      {/* PAPERS */}

      <div className="papers-section">

        <div className="papers-heading">

          <div>
            <span>
              RETRIEVED SOURCES
            </span>

            <h3>
              Research Papers
            </h3>
          </div>

          <div className="paper-count">
            {papers.length} sources
          </div>

        </div>

        {papers.length === 0 ? (

          <div className="no-papers">

            <span>📄</span>

            <h4>
              No external papers returned
            </h4>

            <p>
              Scientific papers returned by
              the retrieval agent will appear
              in this section.
            </p>

          </div>

        ) : (

          <div className="papers-grid">

            {papers.map(
              (paper, index) => (

                <article
                  className="paper-card"
                  key={
                    paper.id ||
                    index
                  }
                >

                  <div className="paper-card-top">

                    <div className="paper-number">
                      {String(
                        index + 1
                      ).padStart(
                        2,
                        "0"
                      )}
                    </div>

                    <div className="paper-relevance">
                      {paper.relevance ||
                        "Relevant"}
                    </div>

                  </div>

                  <h4>
                    {paper.title}
                  </h4>

                  <p className="paper-authors">
                    {paper.authors}
                  </p>

                  <div className="paper-meta">

                    <span>
                      {paper.year}
                    </span>

                    <i></i>

                    <span>
                      {paper.journal}
                    </span>

                  </div>

                  {paper.abstract && (

                    <p className="paper-abstract">
                      {paper.abstract}
                    </p>

                  )}

                  <div className="paper-footer">

                    <span className="paper-source-status">
                      <i></i>

                      Source retrieved
                    </span>

                    {paper.url ? (

                      <a
                        href={paper.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        View Source ↗
                      </a>

                    ) : (

                      <button
                        type="button"
                        disabled
                      >
                        Demo Source
                      </button>

                    )}

                  </div>

                </article>

              )
            )}

          </div>

        )}

      </div>

      {/* VERIFICATION */}

      <div className="verification-card">

        <div className="verification-shield">
          ✓
        </div>

        <div className="verification-content">

          <span>
            VERIFICATION AGENT
          </span>

          <h3>
            {data.verification?.status ||
              "Evidence reviewed"}
          </h3>

          <p>
            {data.verification?.message ||
              "Verification results will appear here."}
          </p>

          <div className="verification-meta">

            <div>
              <strong>
                {data.verification
                  ?.sourcesChecked ??
                  papers.length}
              </strong>

              <span>
                Sources Checked
              </span>
            </div>

            <div>
              <strong>
                {data.verification
                  ?.supportedClaims ??
                  "—"}
              </strong>

              <span>
                Supported Claims
              </span>
            </div>

          </div>

        </div>

      </div>

      {/* RESPONSIBLE AI */}

      <div className="result-disclaimer">

        <span>i</span>

        <p>
          AI-generated research summaries can
          contain errors. Always inspect the
          original scientific publications and
          verify important claims before using
          them in academic work.
        </p>

      </div>

    </section>
  );
}

export default ResearchResults;