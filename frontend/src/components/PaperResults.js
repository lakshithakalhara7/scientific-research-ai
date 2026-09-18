function PaperResults({ papers }) {
  if (!papers || papers.length === 0) return null;

  return (
    <section className="results-section" id="papers">
      <div className="section-top">
        <div>
          <span className="eyebrow">INFORMATION RETRIEVAL</span>
          <h2>Relevant Research Papers</h2>
          <p>
            Papers retrieved based on your research question.
          </p>
        </div>

        <div className="result-count">
          {papers.length}
          <span>papers found</span>
        </div>
      </div>

      <div className="paper-grid">
        {papers.map((paper, index) => (
          <article className="modern-paper" key={paper.id || index}>
            <div className="paper-top">
              <span className="paper-index">
                {String(index + 1).padStart(2, "0")}
              </span>

              {paper.score !== undefined && (
                <span className="score">
                  {typeof paper.score === "number"
                    ? `${(paper.score * 100).toFixed(0)}% match`
                    : paper.score}
                </span>
              )}
            </div>

            <h3>{paper.title || "Untitled Research Paper"}</h3>

            {paper.authors && (
              <p className="authors">
                {paper.authors}
              </p>
            )}

            {paper.abstract && (
              <p className="abstract">
                {paper.abstract}
              </p>
            )}

            <div className="paper-bottom">
              {paper.year && (
                <span>Published {paper.year}</span>
              )}

              {paper.source && paper.source !== "#" && (
                <a
                  href={paper.source}
                  target="_blank"
                  rel="noreferrer"
                >
                  Read paper →
                </a>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default PaperResults;