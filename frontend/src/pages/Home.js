import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

/* =========================================================
   ICONS
========================================================= */

const SearchIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle
      cx="10.8"
      cy="10.8"
      r="6.3"
      stroke="currentColor"
      strokeWidth="1.8"
    />
    <path
      d="M15.5 15.5L20 20"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

const PlusIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M12 5V19M5 12H19"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

const ArrowUpIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M12 19V5M6.5 10.5L12 5L17.5 10.5"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const ArrowRightIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M5 12H19M14 7L19 12L14 17"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const BookIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M4 5.5C6.6 4.8 9.3 5.1 12 6.5V19C9.3 17.6 6.6 17.3 4 18V5.5Z"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
    <path
      d="M20 5.5C17.4 4.8 14.7 5.1 12 6.5V19C14.7 17.6 17.4 17.3 20 18V5.5Z"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
  </svg>
);

const HistoryIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M4.5 8.5A8 8 0 1 1 4 13"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M4.5 4.5V8.5H8.5"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M12 8V12.5L15 14.5"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

const StarIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M12 3.5L14.6 8.8L20.5 9.7L16.2 13.8L17.2 19.7L12 17L6.8 19.7L7.8 13.8L3.5 9.7L9.4 8.8L12 3.5Z"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinejoin="round"
    />
  </svg>
);

const FileIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M6 3.5H14L18 7.5V20.5H6V3.5Z"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
    <path
      d="M14 3.5V8H18"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
    <path
      d="M9 12H15M9 15.5H15"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
    />
  </svg>
);

const LinkIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M9.5 14.5L14.5 9.5"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M7.5 16.5L5.7 18.3C4.2 19.8 1.9 19.8 0.5 18.3"
      transform="translate(3 0)"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M16.5 7.5L18.3 5.7C19.8 4.2 22.1 4.2 23.5 5.7"
      transform="translate(-3 0)"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

const ChartIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M5 19V12M12 19V7M19 19V4"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

const SettingsIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle
      cx="12"
      cy="12"
      r="3"
      stroke="currentColor"
      strokeWidth="1.7"
    />
    <path
      d="M19 13.5V10.5L16.9 9.8C16.7 9.3 16.4 8.8 16 8.3L16.5 6.2L14 4.8L12.5 6.3C12 6.2 11.5 6.2 11 6.3L9.5 4.8L7 6.2L7.5 8.3C7.1 8.8 6.8 9.3 6.6 9.8L4.5 10.5V13.5L6.6 14.2C6.8 14.7 7.1 15.2 7.5 15.7L7 17.8L9.5 19.2L11 17.7C11.5 17.8 12 17.8 12.5 17.7L14 19.2L16.5 17.8L16 15.7C16.4 15.2 16.7 14.7 16.9 14.2L19 13.5Z"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinejoin="round"
    />
  </svg>
);

const ShieldIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M12 3L19 6V11C19 15.7 16.2 19.2 12 21C7.8 19.2 5 15.7 5 11V6L12 3Z"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinejoin="round"
    />
    <path
      d="M9 12L11 14L15.5 9.5"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const SparklesIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path
      d="M12 3L13.3 7.7L18 9L13.3 10.3L12 15L10.7 10.3L6 9L10.7 7.7L12 3Z"
      fill="currentColor"
    />
    <path
      d="M18.5 14L19.2 16.3L21.5 17L19.2 17.7L18.5 20L17.8 17.7L15.5 17L17.8 16.3L18.5 14Z"
      fill="currentColor"
    />
  </svg>
);

/* =========================================================
   DATA
========================================================= */

const suggestions = [
  {
    icon: "✦",
    category: "Artificial Intelligence",
    question: "What are the latest applications of AI?",
  },
  {
    icon: "✚",
    category: "Healthcare Research",
    question: "How is machine learning used in healthcare?",
  },
  {
    icon: "◎",
    category: "Climate Science",
    question: "What role does AI play in climate research?",
  },
  {
    icon: "⌘",
    category: "Machine Learning",
    question: "Compare supervised and unsupervised learning.",
  },
];

/* =========================================================
   HOME
========================================================= */

function Home() {
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  /* =========================================================
     RESEARCH
  ========================================================= */

  const handleResearch = () => {
    if (!query.trim()) return;

    navigate("/research", {
      state: {
        query: query.trim(),
      },
    });
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleResearch();
    }
  };

  const useSuggestion = (question) => {
    setQuery(question);
  };

  /* =========================================================
     UI
  ========================================================= */

  return (
    <div
      className={`home-page ${
        sidebarOpen
          ? "home-sidebar-expanded"
          : "home-sidebar-collapsed"
      }`}
    >
      {/* =====================================================
          ANIMATED BACKGROUND
      ====================================================== */}

      <div className="home-background" aria-hidden="true">
        <div className="home-bg-grid" />

        <div className="home-glow home-glow-one" />
        <div className="home-glow home-glow-two" />
        <div className="home-glow home-glow-three" />

        <span className="home-particle particle-1" />
        <span className="home-particle particle-2" />
        <span className="home-particle particle-3" />
        <span className="home-particle particle-4" />
        <span className="home-particle particle-5" />
        <span className="home-particle particle-6" />
      </div>

      {/* =====================================================
          SIDEBAR
      ====================================================== */}

      <aside
        className={`home-sidebar ${
          sidebarOpen
            ? "home-sidebar-open"
            : "home-sidebar-closed"
        }`}
      >
        {/* SIDEBAR HEADER */}

        <div className="home-sidebar-header">
          <button
            type="button"
            className="home-brand"
            onClick={() => navigate("/")}
          >
            <div className="home-brand-logo-frame">
              <img
                src="/resqmind-logo.jpeg"
                alt="ResQMind"
                className="home-brand-logo"
              />
            </div>

            {sidebarOpen && (
              <div className="home-brand-copy">
                <strong>ResoMind</strong>
                <span>AI Research Intelligence</span>
              </div>
            )}
          </button>

          <button
            type="button"
            className="home-collapse-button"
            onClick={() =>
              setSidebarOpen((current) => !current)
            }
            aria-label={
              sidebarOpen
                ? "Collapse sidebar"
                : "Expand sidebar"
            }
          >
            <span>{sidebarOpen ? "‹" : "›"}</span>
          </button>
        </div>

        {/* NEW RESEARCH */}

        <button
          type="button"
          className="home-new-research"
          onClick={() => {
            setQuery("");
            navigate("/");
          }}
        >
          <span className="home-menu-icon">
            <PlusIcon />
          </span>

          {sidebarOpen && <span>New Research</span>}
        </button>

        {/* =================================================
            MAIN NAVIGATION
        ================================================== */}

        <nav className="home-sidebar-nav">
          <button
            type="button"
            className="home-sidebar-item active"
            onClick={() => navigate("/")}
          >
            <span className="home-sidebar-icon">
              <SearchIcon />
            </span>

            {sidebarOpen && <span>Discover</span>}
          </button>

          <button
            type="button"
            className="home-sidebar-item"
          >
            <span className="home-sidebar-icon">
              <BookIcon />
            </span>

            {sidebarOpen && <span>Library</span>}
          </button>

          <button
            type="button"
            className="home-sidebar-item"
          >
            <span className="home-sidebar-icon">
              <HistoryIcon />
            </span>

            {sidebarOpen && <span>Search History</span>}
          </button>

          <button
            type="button"
            className="home-sidebar-item"
          >
            <span className="home-sidebar-icon">
              <StarIcon />
            </span>

            {sidebarOpen && <span>Saved Papers</span>}
          </button>
        </nav>

        <div className="home-sidebar-divider" />

        {/* =================================================
            RESEARCH TOOLS
        ================================================== */}

        {sidebarOpen && (
          <p className="home-sidebar-label">
            RESEARCH TOOLS
          </p>
        )}

        <nav className="home-sidebar-nav home-tools-nav">
          <button
            type="button"
            className="home-sidebar-item"
          >
            <span className="home-sidebar-icon">
              <FileIcon />
            </span>

            {sidebarOpen && <span>Paper Analyzer</span>}
          </button>

          <button
            type="button"
            className="home-sidebar-item"
          >
            <span className="home-sidebar-icon">
              <LinkIcon />
            </span>

            {sidebarOpen && (
              <span>Source Verification</span>
            )}
          </button>

          <button
            type="button"
            className="home-sidebar-item"
          >
            <span className="home-sidebar-icon">
              <ChartIcon />
            </span>

            {sidebarOpen && (
              <span>Research Insights</span>
            )}
          </button>
        </nav>

        {/* =================================================
            SIDEBAR BOTTOM
        ================================================== */}

        <div className="home-sidebar-bottom">
          <button
            type="button"
            className="home-sidebar-item"
          >
            <span className="home-sidebar-icon">
              <SettingsIcon />
            </span>

            {sidebarOpen && <span>Settings</span>}
          </button>

          {sidebarOpen && (
            <div className="home-assistant-card">
              <div className="home-assistant-icon">
                <SparklesIcon />
              </div>

              <div>
                <strong>ResQMind AI</strong>

                <p>
                  Research smarter with intelligent
                  scientific agents.
                </p>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* =====================================================
          MAIN CONTENT
      ====================================================== */}

      <main className="home-main">
        {/* ===================================================
            HEADER
        ==================================================== */}

        <header className="home-header">
          <button
            type="button"
            className="home-mobile-brand"
            onClick={() => navigate("/")}
          >
            <img
              src="/resqmind-logo.jpeg"
              alt="ResQMind"
            />

            <span>ResQMind</span>
          </button>

          <div className="home-header-right">
            <div className="home-system-status">
              <span />
              AI systems online
            </div>

            <button
              type="button"
              className="home-signin-button"
              onClick={() => navigate("/login")}
            >
              Sign In
            </button>

            <button
              type="button"
              className="home-signup-button"
              onClick={() => navigate("/signup")}
            >
              Get Started
            </button>
          </div>
        </header>

        {/* ===================================================
            PAGE CONTENT
        ==================================================== */}

        <div className="home-content">
          {/* =================================================
              HERO
          ================================================== */}

          <section className="home-hero">
            <div className="home-hero-logo">
              <img
                src="/image01.png"
                alt="ResQMind AI assistant"
              />
            </div>

            <div className="home-hero-badge">
              <span className="home-status-dot" />

              Intelligent Scientific Research Platform
            </div>

            <h1>
              Research smarter.
              <br />
              <span>Discover deeper.</span>
            </h1>

            <p className="home-hero-description">
              Ask scientific questions, explore trusted
              research and let intelligent AI agents retrieve
              evidence, analyze findings and verify
              information for you.
            </p>

            {/* =============================================
                SEARCH
            ============================================== */}

            <div className="home-search-shell">
              <div className="home-search-main">
                <span className="home-search-icon">
                  <SearchIcon />
                </span>

                <textarea
                  rows="1"
                  value={query}
                  onChange={(event) =>
                    setQuery(event.target.value)
                  }
                  onKeyDown={handleKeyDown}
                  placeholder="Ask ResQMind a scientific research question..."
                  aria-label="Research question"
                />

                <div className="home-search-actions">
                  <button
                    type="button"
                    className="home-attach-button"
                    aria-label="Attach file"
                  >
                    <PlusIcon />
                  </button>

                  <button
                    type="button"
                    className="home-research-button"
                    onClick={handleResearch}
                    disabled={!query.trim()}
                    aria-label="Start research"
                  >
                    <ArrowUpIcon />
                  </button>
                </div>
              </div>

              <div className="home-search-footer">
                <span>
                  Ask about papers, scientific concepts,
                  evidence or findings
                </span>

                <span className="home-enter-hint">
                  <kbd>Enter</kbd>
                  to research
                </span>
              </div>
            </div>

            {/* =============================================
                TRUST INDICATORS
            ============================================== */}

            
          </section>

          {/* =================================================
              START EXPLORING
          ================================================== */}

          <section className="home-explore-section">
            <div className="home-section-heading">
              <div>
                <span className="home-section-eyebrow">
                  GET INSPIRED
                </span>

                <h2>Start exploring</h2>
              </div>

              <p>
                Choose a question to begin your research
              </p>
            </div>

            <div className="home-suggestion-grid">
              {suggestions.map((suggestion, index) => (
                <button
                  type="button"
                  key={suggestion.category}
                  className="home-suggestion-card"
                  onClick={() =>
                    useSuggestion(suggestion.question)
                  }
                >
                  <div
                    className={`home-suggestion-icon suggestion-color-${
                      index + 1
                    }`}
                  >
                    {suggestion.icon}
                  </div>

                  <div className="home-suggestion-copy">
                    <strong>
                      {suggestion.category}
                    </strong>

                    <p>{suggestion.question}</p>
                  </div>

                  <span className="home-card-arrow">
                    <ArrowRightIcon />
                  </span>
                </button>
              ))}
            </div>
          </section>

          {/* =================================================
              CAPABILITIES
          ================================================== */}

          <section className="home-capabilities">
            <div className="home-section-heading capability-heading">
              <div>
                <span className="home-section-eyebrow">
                  BUILT FOR RESEARCH
                </span>

                <h2>
                  Your intelligent research workspace
                </h2>
              </div>
            </div>

            <div className="home-capability-grid">
              {/* CAPABILITY 1 */}

              <article className="home-capability-card">
                <div className="home-capability-icon capability-blue">
                  <SearchIcon />
                </div>

                <div>
                  <span className="home-feature-number">
                    01
                  </span>

                  <h3>Intelligent Retrieval</h3>

                  <p>
                    Find relevant scientific literature and
                    information using AI-powered research
                    retrieval.
                  </p>
                </div>
              </article>

              {/* CAPABILITY 2 */}

              <article className="home-capability-card">
                <div className="home-capability-icon capability-purple">
                  <SparklesIcon />
                </div>

                <div>
                  <span className="home-feature-number">
                    02
                  </span>

                  <h3>AI Research Analysis</h3>

                  <p>
                    Break down complex findings and
                    understand important research evidence
                    more efficiently.
                  </p>
                </div>
              </article>

              {/* CAPABILITY 3 */}

              <article className="home-capability-card">
                <div className="home-capability-icon capability-cyan">
                  <ShieldIcon />
                </div>

                <div>
                  <span className="home-feature-number">
                    03
                  </span>

                  <h3>Source Verification</h3>

                  <p>
                    Compare claims with supporting scientific
                    sources and make research more
                    transparent.
                  </p>
                </div>
              </article>
            </div>
          </section>

          {/* =================================================
              CTA
          ================================================== */}

          <section className="home-bottom-cta">
            <div
              className="home-cta-decoration"
              aria-hidden="true"
            />

            <div className="home-cta-content">
              <div className="home-cta-logo">
                <img
                  src="/resqmind-logo.jpeg"
                  alt="ResQMind"
                />
              </div>

              <div>
                <span>
                  RESEARCH WITH CONFIDENCE
                </span>

                <h2>
                  Better questions.
                  <br />
                  <strong>Smarter discoveries.</strong>
                </h2>
              </div>
            </div>

            <button
              type="button"
              className="home-cta-button"
              onClick={() => {
                window.scrollTo({
                  top: 0,
                  behavior: "smooth",
                });
              }}
            >
              Start researching

              <ArrowRightIcon />
            </button>
          </section>

          {/* =================================================
              FOOTER
          ================================================== */}

          <footer className="home-footer">
            <div className="home-footer-brand">
              <span>ResQMind</span>
              <small>AI Research Intelligence</small>
            </div>

            <p>
              AI • NLP • Information Retrieval • Responsible
              AI
            </p>

            <span className="home-footer-copy">
              © 2026 ResQMind
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default Home;