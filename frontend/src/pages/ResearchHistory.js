import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./ResearchHistory.css";

const demoHistory = [
  {
    id: 1,
    question: "What is cloud computing?",
    date: "Today",
    time: "10:42 AM",
    sources: 2,
    status: "Verified",
    category: "Computer Science",
  },
  {
    id: 2,
    question:
      "How is artificial intelligence used in healthcare?",
    date: "Today",
    time: "9:15 AM",
    sources: 4,
    status: "Verified",
    category: "Artificial Intelligence",
  },
  {
    id: 3,
    question:
      "What are the main applications of machine learning?",
    date: "Yesterday",
    time: "4:32 PM",
    sources: 3,
    status: "Partially Verified",
    category: "Machine Learning",
  },
  {
    id: 4,
    question:
      "Explain the current research directions in quantum computing.",
    date: "Sep 18, 2026",
    time: "2:18 PM",
    sources: 5,
    status: "Verified",
    category: "Quantum Computing",
  },
  {
    id: 5,
    question:
      "What technologies can help reduce climate change?",
    date: "Sep 17, 2026",
    time: "11:06 AM",
    sources: 3,
    status: "Verified",
    category: "Environment",
  },
];

function ResearchHistory() {
  const navigate = useNavigate();

  const [search, setSearch] = useState("");

  const filteredHistory = useMemo(() => {
    const value = search.trim().toLowerCase();

    if (!value) {
      return demoHistory;
    }

    return demoHistory.filter((item) => {
      return (
        item.question.toLowerCase().includes(value) ||
        item.category.toLowerCase().includes(value)
      );
    });
  }, [search]);

  const handleOpenResearch = (item) => {
    navigate("/research", {
      state: {
        query: item.question,
      },
    });
  };

  return (
    <div className="history-page">

      {/* =========================================
          SIDEBAR
      ========================================== */}

      <aside className="history-sidebar">

        <div
          className="history-brand"
          onClick={() => navigate("/research")}
        >
          <div className="history-logo">
            <img
              src="/resqmind-logo.jpeg"
              alt="ResoMind"
            />
          </div>

          <div>
            <strong>
              Reso<span>Mind</span>
            </strong>

            <small>
              AI Research Workspace
            </small>
          </div>
        </div>


        <button
          type="button"
          className="history-new-btn"
          onClick={() => navigate("/research")}
        >
          <span>＋</span>
          New Research
        </button>


        <nav className="history-nav">

          <button
            type="button"
            onClick={() => navigate("/research")}
          >
            <span>⌕</span>
            Discover
          </button>


          <button
            type="button"
            onClick={() =>
              navigate("/premium-library")
            }
          >
            <span>▥</span>

            <div className="history-nav-label">
              Research Library

              <small>
                PRO
              </small>
            </div>
          </button>


          <button
            type="button"
            className="active"
          >
            <span>◷</span>
            Research History
          </button>


          <button
            type="button"
            onClick={() =>
              navigate("/saved-papers")
            }
          >
            <span>♡</span>
            Saved Papers
          </button>

        </nav>


        <div className="history-sidebar-label">
          RESEARCH TOOLS
        </div>


        <nav className="history-nav">

          <button
            type="button"
            onClick={() => navigate("/research")}
          >
            <span>▤</span>
            Paper Analyzer
          </button>

          <button
            type="button"
            onClick={() => navigate("/research")}
          >
            <span>♢</span>
            Source Verification
          </button>

          <button
            type="button"
            onClick={() => navigate("/research")}
          >
            <span>▥</span>
            Research Insights
          </button>

          <button
            type="button"
            onClick={() => navigate("/research")}
          >
            <span>✦</span>
            AI Assistant
          </button>

        </nav>


        <div className="history-ai-card">

          <div>
            ✦
          </div>

          <section>
            <strong>
              ResoMind AI
            </strong>

            <span>
              Research smarter with
              intelligent AI agents.
            </span>
          </section>

        </div>

      </aside>


      {/* =========================================
          WORKSPACE
      ========================================== */}

      <div className="history-workspace">

        {/* TOP BAR */}

        <header className="history-topbar">

          <div className="history-online">
            <span></span>
            AI systems online
          </div>

          <button
            type="button"
            className="history-back-btn"
            onClick={() => navigate("/research")}
          >
            Back to Research
            <span>→</span>
          </button>

        </header>


        {/* =====================================
            CONTENT
        ====================================== */}

        <main className="history-content">

          {/* HEADER */}

          <section className="history-heading">

            <div className="history-heading-icon">
              ◷
            </div>

            <div>
              <div className="history-eyebrow">
                YOUR RESEARCH
              </div>

              <h1>
                Research History
              </h1>

              <p>
                Review your previous research
                questions and continue exploring
                your scientific topics.
              </p>
            </div>

          </section>


          {/* SEARCH + STATS */}

          <section className="history-tools">

            <div className="history-search">

              <span>
                ⌕
              </span>

              <input
                type="text"
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                placeholder="Search your research history..."
              />

              {search && (
                <button
                  type="button"
                  onClick={() => setSearch("")}
                >
                  ×
                </button>
              )}

            </div>


            <div className="history-stat">

              <strong>
                {demoHistory.length}
              </strong>

              <span>
                Research sessions
              </span>

            </div>

          </section>


          {/* =====================================
              HISTORY LIST
          ====================================== */}

          <section className="history-list-section">

            <div className="history-list-header">

              <div>
                <span>
                  RECENT ACTIVITY
                </span>

                <h2>
                  Your research
                </h2>
              </div>

              <p>
                {filteredHistory.length}
                {" "}
                {filteredHistory.length === 1
                  ? "result"
                  : "results"}
              </p>

            </div>


            {filteredHistory.length > 0 ? (

              <div className="history-list">

                {filteredHistory.map((item) => (

                  <article
                    className="history-card"
                    key={item.id}
                  >

                    <div className="history-card-icon">
                      ✦
                    </div>


                    <div className="history-card-main">

                      <div className="history-card-top">

                        <span className="history-category">
                          {item.category}
                        </span>

                        <span
                          className={`history-status ${
                            item.status ===
                            "Verified"
                              ? "verified"
                              : "partial"
                          }`}
                        >
                          <i></i>

                          {item.status}
                        </span>

                      </div>


                      <h3>
                        {item.question}
                      </h3>


                      <div className="history-meta">

                        <span>
                          ◷ {item.date}
                        </span>

                        <i></i>

                        <span>
                          {item.time}
                        </span>

                        <i></i>

                        <span>
                          {item.sources} sources
                        </span>

                      </div>

                    </div>


                    <div className="history-card-actions">

                      <button
                        type="button"
                        className="history-open-btn"
                        onClick={() =>
                          handleOpenResearch(item)
                        }
                      >
                        Continue research
                        <span>→</span>
                      </button>

                    </div>

                  </article>

                ))}

              </div>

            ) : (

              <div className="history-empty">

                <div className="history-empty-icon">
                  ⌕
                </div>

                <h3>
                  No research found
                </h3>

                <p>
                  We couldn't find research matching
                  "{search}".
                </p>

                <button
                  type="button"
                  onClick={() => setSearch("")}
                >
                  Clear search
                </button>

              </div>

            )}

          </section>


          {/* RESPONSIBLE AI */}

          <section className="history-ai-notice">

            <div>
              ✓
            </div>

            <section>
              <strong>
                Responsible AI Research
              </strong>

              <p>
                AI-generated research information
                should always be reviewed against
                original scientific sources.
              </p>
            </section>

          </section>

        </main>

      </div>

    </div>
  );
}

export default ResearchHistory;