function AnalysisResult({ analysis }) {
  if (!analysis) return null;

  return (
    <section className="analysis-section" id="analysis">
      <div className="analysis-header">
        <div className="ai-icon">✦</div>

        <div>
          <span className="eyebrow">AI RESEARCH AGENT</span>
          <h2>Research Analysis</h2>
          <p>
            AI-generated insights based on retrieved scientific literature.
          </p>
        </div>

        <span className="ai-badge">AI Generated</span>
      </div>

      <div className="analysis-grid">
        {analysis.summary && (
          <div className="analysis-block">
            <span className="block-number">01</span>
            <div>
              <h3>Summary</h3>
              <p>{analysis.summary}</p>
            </div>
          </div>
        )}

        {analysis.findings && (
          <div className="analysis-block">
            <span className="block-number">02</span>
            <div>
              <h3>Key Findings</h3>
              <p>{analysis.findings}</p>
            </div>
          </div>
        )}

        {analysis.comparison && (
          <div className="analysis-block">
            <span className="block-number">03</span>
            <div>
              <h3>Comparison</h3>
              <p>{analysis.comparison}</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default AnalysisResult;