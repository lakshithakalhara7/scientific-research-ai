import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import DashboardLayout from "../components/DashboardLayout";

import "./PremiumLibrary.css";

import {
  getSavedPapers,
  savePaper,
  removeSavedPaper,
} from "../services/savedPapers";


/* =========================================================
   DEMO PREMIUM PAPERS
========================================================= */

const demoPapers = [
  {
    id: 1,
    title:
      "Artificial Intelligence in Modern Healthcare",
    category:
      "Artificial Intelligence",
    author:
      "ResoMind Research Collection",
    year: "2026",
    pages: 18,
    description:
      "Explore applications of artificial intelligence, clinical decision support and intelligent healthcare systems.",
  },

  {
    id: 2,
    title:
      "Machine Learning for Scientific Discovery",
    category:
      "Machine Learning",
    author:
      "ResoMind Research Collection",
    year: "2026",
    pages: 24,
    description:
      "Research covering machine learning methods and their use in scientific analysis and discovery.",
  },

  {
    id: 3,
    title:
      "Cloud Computing: Models and Applications",
    category:
      "Computer Science",
    author:
      "ResoMind Research Collection",
    year: "2026",
    pages: 14,
    description:
      "An introduction to cloud computing models, characteristics, architectures and research applications.",
  },

  {
    id: 4,
    title:
      "Climate Change and Sustainable Technology",
    category:
      "Environment",
    author:
      "ResoMind Research Collection",
    year: "2025",
    pages: 31,
    description:
      "Scientific research related to climate change, sustainability and emerging environmental technologies.",
  },

  {
    id: 5,
    title:
      "Quantum Computing: Current Research Directions",
    category:
      "Quantum Computing",
    author:
      "ResoMind Research Collection",
    year: "2026",
    pages: 27,
    description:
      "A research overview of quantum computing concepts, algorithms and emerging research directions.",
  },

  {
    id: 6,
    title:
      "AI Applications in Engineering",
    category:
      "Engineering",
    author:
      "ResoMind Research Collection",
    year: "2025",
    pages: 22,
    description:
      "Research into intelligent engineering systems, automation and AI-assisted engineering methods.",
  },
];


/* =========================================================
   CATEGORIES
========================================================= */

const categories = [
  "All",
  "Artificial Intelligence",
  "Machine Learning",
  "Computer Science",
  "Quantum Computing",
  "Engineering",
  "Environment",
];


/* =========================================================
   PREMIUM LIBRARY
========================================================= */

function PremiumLibrary() {

  const navigate = useNavigate();


  /* =======================================================
     STATE
  ======================================================= */

  const [search, setSearch] =
    useState("");

  const [
    selectedCategory,
    setSelectedCategory,
  ] = useState("All");


  const [
  savedPaperIds,
  setSavedPaperIds,
] = useState([]);

const [
  savedPapersLoading,
  setSavedPapersLoading,
] = useState(true);

const [
  savingPaperId,
  setSavingPaperId,
] = useState(null);

const [
  saveError,
  setSaveError,
] = useState("");

/* =======================================================
   LOAD SAVED PAPERS FROM SUPABASE
======================================================= */

useEffect(() => {
  let active = true;

  const loadSavedPapers = async () => {
    try {
      setSavedPapersLoading(true);
      setSaveError("");

      const savedPapers =
        await getSavedPapers();

      if (!active) {
        return;
      }

      const ids = savedPapers.map(
        (paper) =>
          String(paper.paper_id)
      );

      setSavedPaperIds(ids);

    } catch (error) {

      console.error(
        "Unable to load saved papers:",
        error
      );

      if (active) {
        setSaveError(
          error?.message ||
            "Unable to load your saved papers."
        );
      }

    } finally {

      if (active) {
        setSavedPapersLoading(false);
      }
    }
  };

  loadSavedPapers();

  return () => {
    active = false;
  };
}, []);
  /* =======================================================
     FILTER PAPERS
  ======================================================= */

  const filteredPapers =
    useMemo(() => {

      const searchValue =
        search
          .trim()
          .toLowerCase();

      return demoPapers.filter(
        (paper) => {

          const matchesCategory =
            selectedCategory ===
              "All" ||
            paper.category ===
              selectedCategory;


          const matchesSearch =
            !searchValue ||

            paper.title
              .toLowerCase()
              .includes(
                searchValue
              ) ||

            paper.category
              .toLowerCase()
              .includes(
                searchValue
              ) ||

            paper.description
              .toLowerCase()
              .includes(
                searchValue
              );


          return (
            matchesCategory &&
            matchesSearch
          );

        }
      );

    }, [
      search,
      selectedCategory,
    ]);


  /* =======================================================
     ANALYZE PAPER
  ======================================================= */

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


/* =======================================================
   SAVE / UNSAVE PAPER
======================================================= */

const handleSavePaper = async (paper) => {
  const paperId = String(paper.id);

  if (savingPaperId !== null) {
    return;
  }

  const alreadySaved =
    savedPaperIds.includes(paperId);

  try {
    setSavingPaperId(paperId);
    setSaveError("");

    if (alreadySaved) {
      await removeSavedPaper(
        paper.id
      );

      setSavedPaperIds(
        (previous) =>
          previous.filter(
            (id) => id !== paperId
          )
      );

      return;
    }

    await savePaper(paper);

    setSavedPaperIds(
      (previous) => {
        if (
          previous.includes(paperId)
        ) {
          return previous;
        }

        return [
          ...previous,
          paperId,
        ];
      }
    );
  } catch (error) {
    console.error(
      "Unable to update saved paper:",
      error
    );

    setSaveError(
      error?.message ||
        "Unable to update Saved Papers."
    );
  } finally {
    setSavingPaperId(null);
  }
};
/* =======================================================
     PAGE
  ======================================================= */

  return (

    <DashboardLayout activePage="library">
      <div className="premium-library-page">


      {/* =================================================
          WORKSPACE
      ================================================= */}

      <div className="premium-library-workspace">


        {/* TOP BAR */}

        <header className="library-topbar">

          <div>

            <span className="premium-active-dot">
            </span>

            Premium access active

          </div>


          <button
            type="button"
            onClick={() =>
              navigate("/research")
            }
          >

            Back to Research

            <span>
              →
            </span>

          </button>

        </header>


        {/* =================================================
            MAIN
        ================================================= */}

        <main className="library-content">


          {/* =================================================
              HERO
          ================================================= */}

          <section className="library-hero">

            <div className="library-premium-badge">

              ✦ PREMIUM RESEARCH LIBRARY

            </div>


            <h1>

              Discover research.

              <span>
                {" "}Go deeper.
              </span>

            </h1>


            <p>

              Search scientific papers
              from the ResoMind research
              collection and analyze them
              with intelligent AI research
              agents.

            </p>


            {/* SEARCH */}

            <div className="library-search">

              <span className="library-search-icon">

                ⌕

              </span>


              <input
                type="text"
                value={search}
                onChange={
                  (event) =>
                    setSearch(
                      event.target.value
                    )
                }
                placeholder="Search research papers, topics or categories..."
              />


              <button
                type="button"
              >

                Search

              </button>

            </div>


            {/* STATS */}

            <div className="library-stats">


              <div>

                <strong>
                  Premium
                </strong>

                <span>
                  Research access
                </span>

              </div>


              <i></i>


              <div>

                <strong>
                  {demoPapers.length}
                </strong>

                <span>
                  Demo papers
                </span>

              </div>


              <i></i>


              <div>

                <strong>
                  {categories.length - 1}
                </strong>

                <span>
                  Categories
                </span>

              </div>


              <i></i>


              <div>

                <strong>
                  {savedPaperIds.length}
                </strong>

                <span>
                  Saved papers
                </span>

              </div>


            </div>

          </section>


          {/* =================================================
              CATEGORY SECTION
          ================================================= */}

          <section className="library-section">

            <div className="library-section-heading">


              <div>

                <span className="section-label">

                  EXPLORE

                </span>


                <h2>

                  Browse by category

                </h2>

              </div>


              <p>

                Find research from your
                field of interest.

              </p>

            </div>


            <div className="category-buttons">

              {categories.map(
                (category) => (

                  <button
                    type="button"
                    key={category}
                    className={
                      selectedCategory ===
                      category
                        ? "active"
                        : ""
                    }
                    onClick={() =>
                      setSelectedCategory(
                        category
                      )
                    }
                  >

                    {category}

                  </button>

                )
              )}

            </div>

          </section>
{saveError && (
  <div className="library-save-error">
    <strong>
      Saved Papers Error
    </strong>

    <span>
      {saveError}
    </span>
  </div>
)}

          {/* =================================================
              PAPERS
          ================================================= */}

          <section className="library-section papers-section">

            <div className="library-section-heading">


              <div>

                <span className="section-label">

                  RESEARCH COLLECTION

                </span>


                <h2>

                  Research papers

                </h2>

              </div>


              <span className="paper-count">

                {filteredPapers.length}
                {" "}
                papers found

              </span>

            </div>


            {filteredPapers.length > 0 ? (

              <div className="paper-grid">


                {filteredPapers.map(
                  (paper) => {

                    const isSaved =
                      savedPaperIds.includes(
                        String(
                          paper.id
                        )
                      );


                    return (

                      <article
                        className="premium-paper-card"
                        key={paper.id}
                      >


                        {/* CARD TOP */}

                        <div className="paper-card-top">

                          <div className="paper-file-icon">

                            ▤

                          </div>


                          <span className="paper-premium-tag">

                            PREMIUM

                          </span>

                        </div>


                        {/* CATEGORY */}

                        <div className="paper-category">

                          {paper.category}

                        </div>


                        {/* TITLE */}

                        <h3>

                          {paper.title}

                        </h3>


                        {/* DESCRIPTION */}

                        <p className="paper-description">

                          {paper.description}

                        </p>


                        {/* META */}

                        <div className="paper-meta">

                          <span>
                            {paper.year}
                          </span>

                          <i></i>

                          <span>
                            {paper.pages}
                            {" "}
                            pages
                          </span>

                        </div>


                        {/* AUTHOR */}

                        <div className="paper-author">

                          {paper.author}

                        </div>


                        {/* NORMAL ACTIONS */}

                        <div className="paper-actions">


                          <button
                            type="button"
                            className="paper-view-btn"
                          >

                            View paper

                          </button>


                          <button
                            type="button"
                            className="paper-analyze-btn"
                            onClick={() =>
                              handleAnalyze(
                                paper
                              )
                            }
                          >

                            ✦ Analyze with AI

                          </button>

                        </div>


                        {/* SAVE BUTTON */}

                        <button
                          type="button"
                          className={
                            isSaved
                              ? "premium-save-btn saved"
                              : "premium-save-btn"
                          }
                          onClick={() =>
                            handleSavePaper(paper)
                          }
                          disabled={
                            savedPapersLoading ||
                            savingPaperId !== null
                          }
                        >
                          <span>
                            {savingPaperId ===
                            String(paper.id)
                              ? "…"
                              : isSaved
                                ? "♥"
                                : "♡"}
                          </span>

                          {savingPaperId ===
                          String(paper.id)
                            ? "Saving..."
                            : isSaved
                              ? "Saved"
                              : "Save Paper"}
                        </button>


                      </article>

                    );

                  }
                )}

              </div>

            ) : (

              /* EMPTY RESULT */

              <div className="library-empty">

                <div>
                  ⌕
                </div>


                <h3>

                  No papers found

                </h3>


                <p>

                  Try another search term
                  or select a different
                  category.

                </p>


                <button
                  type="button"
                  onClick={() => {

                    setSearch("");

                    setSelectedCategory(
                      "All"
                    );

                  }}
                >

                  Clear filters

                </button>

              </div>

            )}

          </section>


          {/* =================================================
              RESPONSIBLE AI
          ================================================= */}

          <div className="library-responsible-ai">

            <div>
              ✓
            </div>


            <div>

              <strong>

                Responsible AI Research

              </strong>


              <p>

                ResoMind helps you explore
                and analyze research.
                Always review original
                scientific sources before
                relying on AI-generated
                conclusions.

              </p>

            </div>

          </div>


        </main>

      </div>

      </div>
    </DashboardLayout>

  );

}

export default PremiumLibrary;