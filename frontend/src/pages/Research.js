import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import "./Research.css";

function Research() {
  const location = useLocation();
  const navigate = useNavigate();

  const [query, setQuery] = useState(location.state?.query || "");
  const [searched, setSearched] = useState(
    Boolean(location.state?.query)
  );

  const handleSearch = () => {
    if (!query.trim()) return;
    setSearched(true);
  };

  const handleLogout = () => {
    localStorage.removeItem("researchAI_logged_in");
    navigate("/");
  };

  return (
    <div className="research-home">

      {/* BACKGROUND */}
      <div className="research-bg" aria-hidden="true">
        <div className="research-grid"></div>
        <div className="research-glow glow-1"></div>
        <div className="research-glow glow-2"></div>
        <div className="research-glow glow-3"></div>

        <div className="research-particles">
          {Array.from({ length: 18 }).map((_, index) => (
            <span key={index}></span>
          ))}
        </div>
      </div>

      {/* =====================================================
          NAVBAR
      ====================================================== */}

      <header className="research-navbar">

        <button
          className="research-brand"
          onClick={() => navigate("/research")}
        >
            <div className="home-brand-logo-frame">
              <img
                src="/resqmind-logo.jpeg"
                alt="ResQMind"
                className="home-brand-logo"
              />
            </div>

          <div>
            <strong>
              Reso<span>Mind</span>
            </strong>

            <small>
              Intelligent Research Workspace
            </small>
          </div>
        </button>

        <nav className="research-nav">
          <button className="active">
            Home
          </button>

          <button>
            Research
          </button>

          <button>
            Papers
          </button>

          <button>
            History
          </button>
        </nav>

        <div className="research-user">

          <button className="notification-button">
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M18 8A6 6 0 0 0 6 8C6 15 3 16 3 16H21C21 16 18 15 18 8Z"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              <path
                d="M10 20H14"
                stroke="currentColor"
                strokeWidth="1.7"
                strokeLinecap="round"
              />
            </svg>

            <span></span>
          </button>

          <div className="research-avatar">
            R
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>

      </header>

      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="research-main">

        {/* HERO */}

        <section className="research-hero">

          <div className="research-status">
            <span></span>
            AI RESEARCH WORKSPACE
          </div>

          <h1>
            Discover knowledge.
            <br />

            <span>
              Research smarter.
            </span>
          </h1>

          <p className="research-description">
            Search scientific literature, analyze complex
            papers, verify evidence, and transform research
            into meaningful insights with intelligent AI.
          </p>

          {/* SEARCH BOX */}

          <div className="research-search-box">

            <div className="research-search-icon">
              <svg viewBox="0 0 24 24" fill="none">
                <circle
                  cx="11"
                  cy="11"
                  r="7"
                  stroke="currentColor"
                  strokeWidth="1.8"
                />

                <path
                  d="M16.5 16.5L21 21"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                />
              </svg>
            </div>

            <textarea
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="Ask anything about scientific research..."
              onKeyDown={(event) => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey
                ) {
                  event.preventDefault();
                  handleSearch();
                }
              }}
            />

            <div className="research-search-actions">

              <button
                className="search-attachment"
                type="button"
                title="Upload paper"
              >
                <svg viewBox="0 0 24 24" fill="none">
                  <path
                    d="M21.4 11.6L12 21A6 6 0 0 1 3.5 12.5L13 3A4 4 0 0 1 18.7 8.7L9.2 18.2A2 2 0 0 1 6.4 15.4L15 6.8"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinecap="round"
                  />
                </svg>
              </button>

              <button
                className="research-search-button"
                onClick={handleSearch}
                disabled={!query.trim()}
              >
                <span>Research</span>

                <svg viewBox="0 0 24 24" fill="none">
                  <path
                    d="M5 12H19M13 6L19 12L13 18"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>

            </div>

          </div>

          <div className="search-suggestions">

            <span>Try asking:</span>

            <button
              onClick={() =>
                setQuery(
                  "Latest advances in artificial intelligence"
                )
              }
            >
              Artificial Intelligence
            </button>

            <button
              onClick={() =>
                setQuery(
                  "Recent research in quantum computing"
                )
              }
            >
              Quantum Computing
            </button>

            <button
              onClick={() =>
                setQuery(
                  "Machine learning in healthcare"
                )
              }
            >
              Machine Learning
            </button>

          </div>

        </section>


        {/* =====================================================
            CAPABILITIES
        ====================================================== */}

        <section className="capabilities-section">

          <div className="section-heading">

            <div>
              <span className="section-label">
                RESEARCH TOOLS
              </span>

              <h2>
                Everything you need to research
              </h2>

              <p>
                Powerful AI tools designed for scientific
                discovery and evidence-based research.
              </p>
            </div>

            <button className="view-tools">
              View all tools →
            </button>

          </div>


          <div className="capabilities-grid">

            {/* CARD 1 */}

            <article className="capability-card">

              <div className="capability-top">

                <div className="capability-icon blue">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path
                      d="M14 2H6A2 2 0 0 0 4 4V20A2 2 0 0 0 6 22H18A2 2 0 0 0 20 20V8Z"
                      stroke="currentColor"
                      strokeWidth="1.7"
                    />

                    <path
                      d="M14 2V8H20"
                      stroke="currentColor"
                      strokeWidth="1.7"
                    />

                    <path
                      d="M8 13H16M8 17H14"
                      stroke="currentColor"
                      strokeWidth="1.7"
                      strokeLinecap="round"
                    />
                  </svg>
                </div>

                <span className="capability-badge">
                  PDF
                </span>

              </div>

              <h3>
                Analyze a paper
              </h3>

              <p>
                Upload scientific PDFs and let AI extract
                methods, findings, limitations, and key
                research insights.
              </p>

              <button className="capability-action">
                Upload PDF
                <span>→</span>
              </button>

            </article>


            {/* CARD 2 */}

            <article className="capability-card featured">

              <div className="capability-top">

                <div className="capability-icon purple">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 3L14 8L19 10L14 12L12 17L10 12L5 10L10 8L12 3Z"
                      stroke="currentColor"
                      strokeWidth="1.6"
                      strokeLinejoin="round"
                    />

                    <path
                      d="M18 16L19 18L21 19L19 20L18 22L17 20L15 19L17 18L18 16Z"
                      stroke="currentColor"
                      strokeWidth="1.5"
                    />
                  </svg>
                </div>

                <span className="capability-badge ai">
                  AI POWERED
                </span>

              </div>

              <h3>
                Intelligent research
              </h3>

              <p>
                Search across scientific knowledge and
                discover relevant evidence, concepts,
                relationships, and research directions.
              </p>

              <button
                className="capability-action"
                onClick={() =>
                  document
                    .querySelector(
                      ".research-search-box textarea"
                    )
                    ?.focus()
                }
              >
                Start researching
                <span>→</span>
              </button>

            </article>


            {/* CARD 3 */}

            <article className="capability-card">

              <div className="capability-top">

                <div className="capability-icon cyan">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 3L20 6V11C20 16 16.6 20.4 12 22C7.4 20.4 4 16 4 11V6L12 3Z"
                      stroke="currentColor"
                      strokeWidth="1.7"
                    />

                    <path
                      d="M8.5 12L11 14.5L16 9.5"
                      stroke="currentColor"
                      strokeWidth="1.7"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>

                <span className="capability-badge">
                  VERIFIED
                </span>

              </div>

              <h3>
                Evidence verification
              </h3>

              <p>
                Review supporting sources and compare AI
                insights against original scientific
                literature.
              </p>

              <button className="capability-action">
                Explore sources
                <span>→</span>
              </button>

            </article>

          </div>

        </section>


        {/* =====================================================
            SEARCH RESULTS
        ====================================================== */}

        {searched && (

          <section className="research-results">

            <div className="results-heading">

              <div>
                <span>
                  AI RESEARCH
                </span>

                <h2>
                  Research analysis
                </h2>
              </div>

              <div className="ai-status">
                <span></span>
                AI PROCESSING
              </div>

            </div>


            <div className="agent-grid">

              <div className="agent-card">

                <div className="agent-icon">
                  ⌕
                </div>

                <div>
                  <strong>
                    Retrieval Agent
                  </strong>

                  <p>
                    Searching scientific literature
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
                    Extracting research insights
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
                    Checking supporting evidence
                  </p>
                </div>

                <span className="agent-ready">
                  READY
                </span>

              </div>

            </div>


            <div className="query-result-card">

              <div className="query-result-icon">
                ✦
              </div>

              <div>

                <span className="query-label">
                  YOUR RESEARCH QUESTION
                </span>

                <h3>
                  {query}
                </h3>

                <p>
                  Retrieved papers, AI analysis and
                  verified scientific sources will appear
                  here when your backend agents are
                  connected.
                </p>

              </div>

            </div>

          </section>

        )}


        {/* =====================================================
            RESPONSIBLE AI
        ====================================================== */}

        <div className="responsible-notice">

          <div className="notice-icon">
            ✓
          </div>

          <div>
            <strong>
              Responsible AI research
            </strong>

            <p>
              AI-generated insights should always be
              reviewed against the original scientific
              sources.
            </p>
          </div>

        </div>

      </main>

    </div>
  );
}

export default Research;