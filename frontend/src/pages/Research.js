import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  useLocation,
  useNavigate,
} from "react-router-dom";

import "./Research.css";

import PdfUpload from "../components/PdfUpload";
import ResearchResults from "../components/ResearchResults";

import {
  analyzePdf,
  searchResearch,
} from "../services/api";


function Research() {
  const navigate =
    useNavigate();

  const location =
    useLocation();

  const searchRef =
    useRef(null);



  const [query, setQuery] =
    useState(
      location.state?.query || ""
    );

  const [searched, setSearched] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [results, setResults] =
    useState(null);

  const [
    searchError,
    setSearchError,
  ] = useState("");

  const [
    showPdfUpload,
    setShowPdfUpload,
  ] = useState(false);


  /* ==========================================
     SEARCH
  ========================================== */

  const handleSearch =
    async () => {

      if (
        !query.trim() ||
        loading
      ) {
        return;
      }


      setLoading(true);

      setSearched(true);

      setSearchError("");

      setResults(null);


      try {

        const data =
          await searchResearch(
            query
          );


        setResults(data);


        setTimeout(() => {

          document
            .querySelector(
              ".research-results"
            )
            ?.scrollIntoView({
              behavior:
                "smooth",

              block:
                "start",
            });

        }, 150);

      } catch (error) {

        console.error(
          "Research error:",
          error
        );


        setSearchError(
          "Unable to complete the research request. Please try again."
        );

      } finally {

        setLoading(false);

      }
    };


  /* ==========================================
     PDF ANALYSIS
  ========================================== */

  const handlePdfAnalysis =
    async (file) => {

      if (!file) {
        return;
      }


      console.log(
        "PDF selected:",
        file
      );


      setShowPdfUpload(false);

      setLoading(true);

      setSearched(true);

      setSearchError("");

      setResults(null);


      try {

        const data =
          await analyzePdf(
            file
          );


        setResults(data);


        setTimeout(() => {

          document
            .querySelector(
              ".research-results"
            )
            ?.scrollIntoView({
              behavior:
                "smooth",

              block:
                "start",
            });

        }, 150);

      } catch (error) {

        console.error(
          "PDF error:",
          error
        );


        setSearchError(
          "The PDF could not be analyzed. Please try again."
        );

      } finally {

        setLoading(false);

      }
    };


  /* ==========================================
     SEARCH FOCUS
  ========================================== */

  const focusResearch =
    () => {

      searchRef.current
        ?.scrollIntoView({
          behavior:
            "smooth",

          block:
            "center",
        });


      setTimeout(() => {

        searchRef.current
          ?.focus();

      }, 400);
    };


  /* ==========================================
     INITIAL QUERY
  ========================================== */

  useEffect(() => {

    if (
      location.state?.query
    ) {

      setQuery(
        location.state.query
      );

    }

  }, [location.state]);


  return (
    <div className="research-home">

      {/* BACKGROUND */}

      <div
        className="research-bg"
        aria-hidden="true"
      >

        <div className="research-grid"></div>

        <div className="research-glow glow-1"></div>

        <div className="research-glow glow-2"></div>

        <div className="research-glow glow-3"></div>

      </div>


      {/* NAVBAR */}

      <header className="research-navbar">

        <button
          className="research-brand"
          onClick={() =>
            navigate(
              "/research"
            )
          }
        >

          <div className="home-brand-logo-frame">

            <img
              src="/resqmind-logo.jpeg"
              alt="ResoMind"
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

          <button
            className="active"
            onClick={() => {

              window.scrollTo({
                top: 0,
                behavior:
                  "smooth",
              });

            }}
          >
            Home
          </button>


          <button
            onClick={
              focusResearch
            }
          >
            Research
          </button>


          <button
            onClick={() => {

              if (results) {

                document
                  .querySelector(
                    ".papers-section"
                  )
                  ?.scrollIntoView({
                    behavior:
                      "smooth",
                  });

              } else {

                focusResearch();

              }

            }}
          >
            Papers
          </button>


          <button
            onClick={() => {

              alert(
                "Research history will be connected in the next stage."
              );

            }}
          >
            History
          </button>

        </nav>


        <div className="research-user">

          <div className="research-avatar">
            R
          </div>


          <button
            className="logout-button"
            onClick={() => {

              localStorage.removeItem(
                "researchAI_logged_in"
              );

              navigate("/");

            }}
          >
            Logout
          </button>

        </div>

      </header>


      {/* MAIN */}

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

            Search scientific literature,
            analyze research papers,
            investigate evidence and
            transform complex scientific
            information into meaningful
            insights.

          </p>


          {/* SEARCH BOX */}

          <div className="research-search-box">

            <div className="research-search-icon">

              <svg
                viewBox="0 0 24 24"
                fill="none"
              >

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
              ref={searchRef}
              value={query}
              placeholder="Ask anything about scientific research..."
              onChange={(event) =>
                setQuery(
                  event.target.value
                )
              }
              onKeyDown={(event) => {

                if (
                  event.key ===
                    "Enter" &&
                  !event.shiftKey
                ) {

                  event.preventDefault();

                  handleSearch();

                }

              }}
            />


            <div className="research-search-actions">

              {/* PDF ICON */}

              <button
                type="button"
                className="search-attachment"
                title="Upload PDF"
                onClick={() =>
                  setShowPdfUpload(
                    true
                  )
                }
              >

                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                >

                  <path
                    d="M21.4 11.6L12 21A6 6 0 0 1 3.5 12.5L13 3A4 4 0 0 1 18.7 8.7L9.2 18.2A2 2 0 0 1 6.4 15.4L15 6.8"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinecap="round"
                  />

                </svg>

              </button>


              {/* SEARCH BUTTON */}

              <button
                className="research-search-button"
                type="button"
                disabled={
                  !query.trim() ||
                  loading
                }
                onClick={
                  handleSearch
                }
              >

                {loading ? (

                  <>
                    <span>
                      Working...
                    </span>

                    <div className="button-loader"></div>
                  </>

                ) : (

                  <>
                    <span>
                      Research
                    </span>

                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                    >

                      <path
                        d="M5 12H19M13 6L19 12L13 18"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />

                    </svg>

                  </>

                )}

              </button>

            </div>

          </div>


          {/* SUGGESTIONS */}

          <div className="search-suggestions">

            <span>
              Try asking:
            </span>


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
                  "Machine learning applications in healthcare"
                )
              }
            >
              Machine Learning
            </button>

          </div>

        </section>


        {/* TOOLS */}

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
                Intelligent tools designed
                for scientific discovery,
                analysis and evidence
                verification.
              </p>

            </div>

          </div>


          <div className="capabilities-grid">


            {/* PDF */}

            <article className="capability-card">

              <div className="capability-top">

                <div className="capability-icon blue">
                  📄
                </div>

                <span className="capability-badge">
                  PDF
                </span>

              </div>


              <h3>
                Analyze a paper
              </h3>


              <p>
                Upload scientific PDFs and
                analyze methods, findings,
                limitations and important
                research concepts.
              </p>


              <button
                type="button"
                className="capability-action"
                onClick={() =>
                  setShowPdfUpload(
                    true
                  )
                }
              >
                Upload PDF

                <span>→</span>
              </button>

            </article>


            {/* RESEARCH */}

            <article className="capability-card featured">

              <div className="capability-top">

                <div className="capability-icon purple">
                  ✦
                </div>

                <span className="capability-badge ai">
                  AI POWERED
                </span>

              </div>


              <h3>
                Intelligent research
              </h3>


              <p>
                Ask scientific questions
                and discover relevant
                research, evidence and
                structured AI insights.
              </p>


              <button
                type="button"
                className="capability-action"
                onClick={
                  focusResearch
                }
              >
                Start Researching

                <span>→</span>
              </button>

            </article>


            {/* VERIFICATION */}

            <article className="capability-card">

              <div className="capability-top">

                <div className="capability-icon cyan">
                  ✓
                </div>

                <span className="capability-badge">
                  VERIFIED
                </span>

              </div>


              <h3>
                Evidence verification
              </h3>


              <p>
                Compare AI-generated
                research insights against
                supporting scientific
                evidence.
              </p>


              <button
                type="button"
                className="capability-action"
                onClick={() => {

                  if (results) {

                    document
                      .querySelector(
                        ".verification-card"
                      )
                      ?.scrollIntoView({
                        behavior:
                          "smooth",
                      });

                  } else {

                    focusResearch();

                  }

                }}
              >
                Verify Research

                <span>→</span>
              </button>

            </article>

          </div>

        </section>


        {/* ERROR */}

        {searchError && (

          <div className="research-error">

            <span>!</span>

            <div>

              <strong>
                Something went wrong
              </strong>

              <p>
                {searchError}
              </p>

            </div>

          </div>

        )}


        {/* LOADING */}

        {loading && (

          <section className="research-processing">

            <div className="processing-orbit">

              <div className="processing-core">
                ✦
              </div>

            </div>


            <h3>
              Research agents are working
            </h3>


            <p>
              Retrieving information,
              analyzing research and
              verifying evidence...
            </p>


            <div className="processing-steps">

              <span>
                <i></i>
                Retrieval
              </span>

              <span>
                <i></i>
                Analysis
              </span>

              <span>
                <i></i>
                Verification
              </span>

            </div>

          </section>

        )}


        {/* RESULTS */}

        {searched &&
          !loading &&
          results && (

            <ResearchResults
              data={results}
              query={query}
            />

          )}


        {/* RESPONSIBLE AI */}

        <div className="responsible-notice">

          <div className="notice-icon">
            ✓
          </div>


          <div>

            <strong>
              Responsible AI Research
            </strong>

            <p>
              AI-generated research
              information should always be
              reviewed against original
              scientific sources.
            </p>

          </div>

        </div>

      </main>


      {/* PDF MODAL */}

      {showPdfUpload && (

        <PdfUpload
          onClose={() =>
            setShowPdfUpload(
              false
            )
          }
          onAnalyze={
            handlePdfAnalysis
          }
        />

      )}

    </div>
  );
}


export default Research;





