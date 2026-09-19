import "./ResearchResults.css";

function ResearchResults({ data, query }) {
  if (!data) {
    return null;
  }

  // =========================================================
  // REAL BACKEND RESPONSE
  // =========================================================

  const analysis = data.analysis || {};
  const verification = data.verification || {};
  const sources = data.sources || [];

  const findings = analysis.key_findings || [];
  const methods = analysis.methods || [];
  const warnings = verification.warnings || [];

  const verificationStatus =
    verification.overall_status || "NOT VERIFIED";

  const formatStatus = (status) => {
    return String(status || "")
      .replaceAll("_", " ")
      .toLowerCase()
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };

  return (
    <section className="research-results">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="results-heading">

        <div>
          <span>AI RESEARCH</span>

          <h2>Research Analysis</h2>
        </div>

        <div className="ai-status">
          <span></span>
          ANALYSIS COMPLETE
        </div>

      </div>

      {/* =====================================================
          AGENTS
      ===================================================== */}

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
            {formatStatus(verificationStatus)}
          </span>

        </div>

      </div>

      {/* =====================================================
          QUESTION
      ===================================================== */}

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

      {/* =====================================================
          ANALYSIS
      ===================================================== */}

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
          {analysis.summary ||
            "No summary was returned."}
        </p>

        {/* KEY FINDINGS */}

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

        {/* METHODS */}

        {methods.length > 0 && (

          <div className="key-findings">

            <h4>
              Methods / Models
            </h4>

            {methods.map(
              (method, index) => (

                <div
                  className="finding-item"
                  key={index}
                >

                  <span>
                    {index + 1}
                  </span>

                  <p>
                    {method}
                  </p>

                </div>

              )
            )}

          </div>

        )}

        {/* CONCLUSION */}

        {analysis.conclusion && (

          <div className="key-findings">

            <h4>
              Conclusion
            </h4>

            <p className="analysis-summary">
              {analysis.conclusion}
            </p>

          </div>

        )}

      </div>

      {/* =====================================================
          RETRIEVED SOURCES
      ===================================================== */}

      <div className="papers-section">

        <div className="papers-heading">

          <div>
            <span>
              RETRIEVED SOURCES
            </span>

            <h3>
              Research Sources
            </h3>
          </div>

          <div className="paper-count">
            {sources.length}{" "}
            {sources.length === 1
              ? "source"
              : "sources"}
          </div>

        </div>

        {sources.length === 0 ? (

          <div className="no-papers">

            <span>📄</span>

            <h4>
              No research sources returned
            </h4>

            <p>
              Sources returned by the retrieval
              agent will appear in this section.
            </p>

          </div>

        ) : (

          <div className="papers-grid">

            {sources.map(
              (source, index) => (

                <article
                  className="paper-card"
                  key={`${source.filename}-${source.page_number}-${source.chunk_number}-${index}`}
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
                      Retrieved
                    </div>

                  </div>

                  <h4>
                    {source.filename ||
                      "Research document"}
                  </h4>

                  <p className="paper-authors">
                    Retrieved evidence source
                  </p>

                  <div className="paper-meta">

                    <span>
                      Page{" "}
                      {source.page_number ??
                        "—"}
                    </span>

                    <i></i>

                    <span>
                      Chunk{" "}
                      {source.chunk_number ??
                        "—"}
                    </span>

                  </div>

                  {source.retrieval_score !=
                    null && (

                    <p className="paper-abstract">
                      Retrieval score:{" "}
                      {Number(
                        source.retrieval_score
                      ).toFixed(4)}
                    </p>

                  )}

                  <div className="paper-footer">

                    <span className="paper-source-status">
                      <i></i>
                      Source retrieved
                    </span>

                  </div>

                </article>

              )
            )}

          </div>

        )}

      </div>

      {/* =====================================================
          VERIFICATION
      ===================================================== */}

      <div className="verification-card">

        <div className="verification-shield">
          ✓
        </div>

        <div className="verification-content">

          <span>
            VERIFICATION AGENT
          </span>

          <h3>
            {formatStatus(
              verificationStatus
            )}
          </h3>

          <p>
            {verification.total_claims > 0
              ? `${verification.verified_claims ?? 0} of ${verification.total_claims} claims were fully verified against the retrieved evidence.`
              : "No claims were available for verification."}
          </p>

          <div className="verification-meta">

            <div>

              <strong>
                {sources.length}
              </strong>

              <span>
                Sources Checked
              </span>

            </div>

            <div>

              <strong>
                {verification.verified_claims ??
                  0}
              </strong>

              <span>
                Verified Claims
              </span>

            </div>

            <div>

              <strong>
                {verification.partially_supported_claims ??
                  0}
              </strong>

              <span>
                Partially Supported
              </span>

            </div>

            <div>

              <strong>
                {verification.insufficient_evidence_claims ??
                  0}
              </strong>

              <span>
                Insufficient Evidence
              </span>

            </div>

          </div>

          {/* WARNINGS */}

          {warnings.length > 0 && (

            <div className="key-findings">

              <h4>
                Verification Warnings
              </h4>

              {warnings.map(
                (warning, index) => (

                  <div
                    className="finding-item"
                    key={index}
                  >

                    <span>!</span>

                    <p>
                      {warning.message ||
                        warning.claim ||
                        "Verification warning"}
                    </p>

                  </div>

                )
              )}

            </div>

          )}

        </div>

      </div>

      {/* =====================================================
          RESPONSIBLE AI
      ===================================================== */}

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