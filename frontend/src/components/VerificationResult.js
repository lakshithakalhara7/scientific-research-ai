function VerificationResult({ verification }) {
  if (!verification || verification.length === 0) return null;

  return (
    <section className="verification-section" id="verification">
      <div className="section-top">
        <div>
          <span className="eyebrow">TRUST & SAFETY</span>
          <h2>Source Verification</h2>
          <p>
            Claims are checked against supporting research sources.
          </p>
        </div>

        <div className="verified-icon">✓</div>
      </div>

      <div className="verification-list">
        {verification.map((item, index) => {
          const verified = item.status === "verified";

          return (
            <div
              className={`verification-row ${
                verified ? "verified" : "warning"
              }`}
              key={index}
            >
              <div className="verification-symbol">
                {verified ? "✓" : "!"}
              </div>

              <div className="verification-content">
                <div className="verification-title">
                  <h3>{item.claim || "Research claim"}</h3>

                  <span>
                    {verified ? "Verified" : "Review Required"}
                  </span>
                </div>

                <p>
                  {item.explanation ||
                    "No explanation provided."}
                </p>

                {item.source && item.source !== "#" && (
                  <a
                    href={item.source}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View supporting evidence →
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default VerificationResult;