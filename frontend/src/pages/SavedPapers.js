import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  getSavedPapers,
  removeSavedPaper,
} from "../services/savedPapers";

import "./SavedPapers.css";


function SavedPapers() {

  const navigate = useNavigate();

  const [papers, setPapers] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [
    removingId,
    setRemovingId,
  ] = useState(null);


  /* ================================================
     LOAD SAVED PAPERS
  ================================================ */

  useEffect(() => {

    let active = true;

    const loadPapers = async () => {

      try {

        setLoading(true);
        setError("");

        const data =
          await getSavedPapers();

        if (active) {
          setPapers(data);
        }

      } catch (err) {

        console.error(
          "Saved papers load error:",
          err
        );

        if (active) {
          setError(
            err?.message ||
            "Unable to load saved papers."
          );
        }

      } finally {

        if (active) {
          setLoading(false);
        }

      }

    };

    loadPapers();

    return () => {
      active = false;
    };

  }, []);


  /* ================================================
     REMOVE PAPER
  ================================================ */

  const handleRemove = async (
    paper
  ) => {

    try {

      setRemovingId(
        String(paper.paper_id)
      );

      setError("");

      await removeSavedPaper(
        paper.paper_id
      );

      setPapers(
        (previous) =>
          previous.filter(
            (item) =>
              String(item.paper_id) !==
              String(paper.paper_id)
          )
      );

    } catch (err) {

      console.error(
        "Remove saved paper error:",
        err
      );

      setError(
        err?.message ||
        "Unable to remove the paper."
      );

    } finally {

      setRemovingId(null);

    }

  };


  /* ================================================
     ANALYZE
  ================================================ */

  const handleAnalyze = (
    paper
  ) => {

    navigate(
      "/research",
      {
        state: {
          query:
            `Summarize and analyze the research about ${paper.title}`,
        },
      }
    );

  };


  /* ================================================
     PAGE
  ================================================ */

  return (

    <div className="saved-page">

      {/* SIDEBAR */}

      <aside className="saved-sidebar">

        <div
          className="saved-brand"
          onClick={() =>
            navigate("/research")
          }
        >

          <img
            src="/resqmind-logo.jpeg"
            alt="ResoMind"
          />

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
          className="saved-new-button"
          onClick={() =>
            navigate("/research")
          }
        >
          ＋ New Research
        </button>


        <nav className="saved-nav">

          <button
            type="button"
            onClick={() =>
              navigate("/research")
            }
          >
            <span>⌕</span>
            Discover
          </button>


          <button
            type="button"
            onClick={() =>
              navigate(
                "/premium-library"
              )
            }
          >
            <span>▥</span>
            Research Library
          </button>


          <button
            type="button"
            onClick={() =>
              navigate(
                "/research-history"
              )
            }
          >
            <span>◷</span>
            Research History
          </button>


          <button
            type="button"
            className="active"
          >
            <span>♥</span>
            Saved Papers
          </button>

        </nav>


        <div className="saved-sidebar-bottom">

          <button
            type="button"
            onClick={() =>
              navigate("/settings")
            }
          >
            ⚙ Settings
          </button>

        </div>

      </aside>


      {/* MAIN */}

      <main className="saved-main">

        <header className="saved-header">

          <div>

            <span className="saved-eyebrow">
              RESEARCH COLLECTION
            </span>

            <h1>
              Saved Papers
            </h1>

            <p>
              Your personal collection of
              saved research papers.
            </p>

          </div>


          <button
            type="button"
            onClick={() =>
              navigate(
                "/premium-library"
              )
            }
          >
            Browse Library →
          </button>

        </header>


        {/* ERROR */}

        {error && (

          <div className="saved-error">

            <strong>
              Unable to load Saved Papers
            </strong>

            <span>
              {error}
            </span>

          </div>

        )}


        {/* LOADING */}

        {loading && (

          <div className="saved-loading">

            <div className="saved-spinner" />

            <strong>
              Loading saved papers...
            </strong>

          </div>

        )}


        {/* EMPTY */}

        {!loading &&
          !error &&
          papers.length === 0 && (

            <div className="saved-empty">

              <div className="saved-empty-icon">
                ♡
              </div>

              <h2>
                No saved papers yet
              </h2>

              <p>
                Browse the Premium Research
                Library and save papers you
                want to revisit later.
              </p>

              <button
                type="button"
                onClick={() =>
                  navigate(
                    "/premium-library"
                  )
                }
              >
                Browse Research Library
              </button>

            </div>

          )}


        {/* PAPERS */}

        {!loading &&
          papers.length > 0 && (

            <section className="saved-content">

              <div className="saved-summary">

                <div>

                  <span>
                    SAVED COLLECTION
                  </span>

                  <h2>
                    Your research papers
                  </h2>

                </div>

                <strong>
                  {papers.length}{" "}
                  {papers.length === 1
                    ? "paper"
                    : "papers"}
                </strong>

              </div>


              <div className="saved-grid">

                {papers.map(
                  (paper) => (

                    <article
                      className="saved-card"
                      key={paper.id}
                    >

                      <div className="saved-card-top">

                        <div className="saved-file-icon">
                          ▤
                        </div>

                        <span className="saved-badge">
                          SAVED
                        </span>

                      </div>


                      <span className="saved-category">
                        {paper.category ||
                          "Research"}
                      </span>


                      <h3>
                        {paper.title}
                      </h3>


                      <p className="saved-description">
                        {paper.description ||
                          "Saved research paper from the ResoMind collection."}
                      </p>


                      <div className="saved-meta">

                        {paper.year && (
                          <span>
                            {paper.year}
                          </span>
                        )}

                        {paper.year &&
                          paper.pages && (
                            <i />
                          )}

                        {paper.pages && (
                          <span>
                            {paper.pages} pages
                          </span>
                        )}

                      </div>


                      {paper.author && (

                        <div className="saved-author">
                          {paper.author}
                        </div>

                      )}


                      <div className="saved-actions">

                        <button
                          type="button"
                          className="saved-analyze"
                          onClick={() =>
                            handleAnalyze(
                              paper
                            )
                          }
                        >
                          ✦ Analyze with AI
                        </button>


                        <button
                          type="button"
                          className="saved-remove"
                          disabled={
                            removingId ===
                            String(
                              paper.paper_id
                            )
                          }
                          onClick={() =>
                            handleRemove(
                              paper
                            )
                          }
                        >

                          {removingId ===
                          String(
                            paper.paper_id
                          )
                            ? "Removing..."
                            : "♡ Remove"}

                        </button>

                      </div>

                    </article>

                  )
                )}

              </div>

            </section>

          )}

      </main>

    </div>

  );

}

export default SavedPapers;