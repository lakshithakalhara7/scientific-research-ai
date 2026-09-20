import { useNavigate } from "react-router-dom";
import "./Premium.css";

function Premium() {
  const navigate = useNavigate();

  const handleStartTrial = () => {
    // We will create this payment route in a later step.
    navigate("/payment");
  };

  return (
    <div className="premium-page">

      <div className="premium-topbar">
        <button
          className="premium-back-btn"
          onClick={() => navigate("/research")}
        >
          ← Back to Research
        </button>

        <div className="premium-brand">
          Reso<span>Mind</span>
        </div>
      </div>

      <main className="premium-container">

        <div className="premium-badge">
          ✦ RESOMIND PREMIUM
        </div>

        <h1>
          Unlock your complete
          <span> research library</span>
        </h1>

        <p className="premium-description">
          Search research papers stored in ResoMind,
          explore papers by category and analyze them
          using our intelligent AI research agents.
        </p>

        <div className="premium-offer">
          <span>LIMITED OFFER</span>
          <strong>Get your first month FREE</strong>
          <p>
            Explore all Premium features for one month.
          </p>
        </div>

        <div className="premium-card">

          <div className="premium-plan-header">
            <div>
              <span className="plan-name">
                Premium Researcher
              </span>

              <h2>
                $4.99
                <small>/ month</small>
              </h2>
            </div>

            <div className="free-month">
              1 MONTH FREE
            </div>
          </div>

          <div className="premium-divider" />

          <div className="premium-features">

            <div>
              <span>✓</span>
              <p>
                <strong>Research PDF Library</strong>
                Search papers available in ResoMind
              </p>
            </div>

            <div>
              <span>✓</span>
              <p>
                <strong>Research Categories</strong>
                Browse AI, Computing, Medicine,
                Engineering and more
              </p>
            </div>

            <div>
              <span>✓</span>
              <p>
                <strong>AI Paper Analysis</strong>
                Analyze library papers with your
                research agents
              </p>
            </div>

            <div>
              <span>✓</span>
              <p>
                <strong>Source Verification</strong>
                Verify AI-generated claims against
                research evidence
              </p>
            </div>

            <div>
              <span>✓</span>
              <p>
                <strong>Advanced Search</strong>
                Search and filter the research library
              </p>
            </div>

          </div>

          <button
            className="start-trial-btn"
            onClick={handleStartTrial}
          >
            Start 1 Month Free Trial →
          </button>

          <p className="premium-payment-note">
            🔒 Secure payment • Cancel anytime
          </p>

        </div>

        <div className="premium-bottom-note">
          <span>🛡</span>

          <div>
            <strong>
              Your research remains private
            </strong>

            <p>
              ResoMind follows responsible AI and
              privacy-focused research practices.
            </p>
          </div>
        </div>

      </main>

    </div>
  );
}

export default Premium;