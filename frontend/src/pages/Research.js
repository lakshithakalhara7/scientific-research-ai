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
  uploadDocument,
  searchResearch,
} from "../services/api";

import { supabase } from "../services/supabase";


/* =========================================================
   ICON COMPONENT
========================================================= */

function Icon({
  name,
  size = 20,
}) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": "true",
  };

  const paths = {
    plus: (
      <>
        <path d="M12 5v14" />
        <path d="M5 12h14" />
      </>
    ),

    search: (
      <>
        <circle
          cx="11"
          cy="11"
          r="7"
        />
        <path d="m20 20-3.7-3.7" />
      </>
    ),

    book: (
      <>
        <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22z" />
        <path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22z" />
      </>
    ),

    history: (
      <>
        <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
        <path d="M3 3v5h5" />
        <path d="M12 7v5l3 2" />
      </>
    ),

    bookmark: (
      <path d="M6 4.5A1.5 1.5 0 0 1 7.5 3h9A1.5 1.5 0 0 1 18 4.5V21l-6-4-6 4z" />
    ),

    file: (
      <>
        <path d="M6 2h8l4 4v16H6z" />
        <path d="M14 2v5h5" />
        <path d="M9 12h6M9 16h6" />
      </>
    ),

    shield: (
      <>
        <path d="M12 3 5 6v5c0 4.8 2.9 8.2 7 10 4.1-1.8 7-5.2 7-10V6z" />
        <path d="m9.5 12 1.7 1.7 3.5-3.8" />
      </>
    ),

    chart: (
      <>
        <path d="M5 20V10" />
        <path d="M10 20V4" />
        <path d="M15 20v-7" />
        <path d="M20 20V7" />
      </>
    ),

    sparkle: (
      <>
        <path d="m12 3 1.2 3.8L17 8l-3.8 1.2L12 13l-1.2-3.8L7 8l3.8-1.2z" />
        <path d="m18.5 14 .7 2.3 2.3.7-2.3.7-.7 2.3-.7-2.3-2.3-.7 2.3-.7z" />
      </>
    ),

    settings: (
      <>
        <circle
          cx="12"
          cy="12"
          r="3"
        />

        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21h-4v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3.1 14H3v-4h.1A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3.1V3h4v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1H21v4h-.1a1.7 1.7 0 0 0-1.5 1z" />
      </>
    ),

    paperclip: (
      <path d="m20.5 11.5-8.9 8.9a5 5 0 0 1-7.1-7.1l9.5-9.5a3.5 3.5 0 1 1 5 5l-9.5 9.5a2 2 0 0 1-2.8-2.8l8.8-8.8" />
    ),

    arrow: (
      <>
        <path d="M5 12h14" />
        <path d="m14 7 5 5-5 5" />
      </>
    ),

    check: (
      <path d="m7 12 3 3 7-7" />
    ),

    bulb: (
      <>
        <path d="M9 18h6" />
        <path d="M10 22h4" />
        <path d="M8.5 14.5A6 6 0 1 1 15.5 14.5c-.9.7-1.5 1.5-1.5 2.5h-4c0-1-.6-1.8-1.5-2.5z" />
      </>
    ),

    logout: (
      <>
        <path d="M10 17l5-5-5-5" />
        <path d="M15 12H3" />
        <path d="M21 19V5a2 2 0 0 0-2-2h-6" />
      </>
    ),
  };

  return (
    <svg {...common}>
      {paths[name]}
    </svg>
  );
}


/* =========================================================
   RESEARCH PAGE
========================================================= */

function Research() {
  const navigate =
    useNavigate();

  const location =
    useLocation();

  const searchRef =
    useRef(null);

  const profileRef =
    useRef(null);


  /* =========================================================
     STATE
  ========================================================= */

  const [
    query,
    setQuery,
  ] = useState(
    location.state?.query || ""
  );

  const [
    searched,
    setSearched,
  ] = useState(
    location.state?.searched || false
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    results,
    setResults,
  ] = useState(
    location.state?.results || null
  );

  const [
    searchError,
    setSearchError,
  ] = useState("");

  const [
    showPdfUpload,
    setShowPdfUpload,
  ] = useState(false);

  const [
    uploadedDocument,
    setUploadedDocument,
  ] = useState(null);

  const [
    uploadMessage,
    setUploadMessage,
  ] = useState("");

  const [
    currentUser,
    setCurrentUser,
  ] = useState(null);

  const [
    userName,
    setUserName,
  ] = useState("");

  const [
    userInitial,
    setUserInitial,
  ] = useState("U");

  const [
    sidebarCollapsed,
    setSidebarCollapsed,
  ] = useState(false);

  const [
    profileOpen,
    setProfileOpen,
  ] = useState(false);


  /* =========================================================
     LOAD LOGGED-IN USER
  ========================================================= */

  useEffect(() => {
    const loadCurrentUser =
      async () => {
        try {
          const {
            data: { user },
            error,
          } =
            await supabase.auth.getUser();

          if (error) {
            throw error;
          }

          if (!user) {
            navigate("/login");
            return;
          }

          setCurrentUser(user);

          const fullName =
            user.user_metadata?.full_name ||
            user.user_metadata?.name ||
            user.user_metadata?.first_name ||
            "";

          const email =
            user.email || "";

          const firstName =
            fullName.trim()
              ? fullName
                  .trim()
                  .split(" ")[0]
              : email.split("@")[0];

          setUserName(firstName);

          const initial =
            firstName?.charAt(0) ||
            email?.charAt(0) ||
            "U";

          setUserInitial(
            initial.toUpperCase()
          );
        } catch (error) {
          console.error(
            "Unable to load user:",
            error
          );
        }
      };

    loadCurrentUser();
  }, [navigate]);


  /* =========================================================
     INITIAL QUERY
  ========================================================= */

  useEffect(() => {
    if (location.state?.query) {
      setQuery(
        location.state.query
      );
    }
  }, [location.state]);


  /* =========================================================
     CLOSE PROFILE WHEN CLICKING OUTSIDE
  ========================================================= */

  useEffect(() => {
    const handleOutsideClick =
      (event) => {
        if (
          profileRef.current &&
          !profileRef.current.contains(
            event.target
          )
        ) {
          setProfileOpen(false);
        }
      };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);


  /* =========================================================
     RESEARCH FOCUS
  ========================================================= */

  const focusResearch = () => {
    searchRef.current
      ?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

    setTimeout(() => {
      searchRef.current?.focus();
    }, 350);
  };


  /* =========================================================
     SEARCH
  ========================================================= */

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
      setUploadMessage("");
      setResults(null);

      try {
        const {
          data: { session },
          error: sessionError,
        } =
          await supabase.auth.getSession();

        if (sessionError) {
          throw sessionError;
        }

        if (
          !session?.access_token
        ) {
          navigate("/login");
          return;
        }

        const documentId =
          uploadedDocument?.id ||
          null;

        const data =
          await searchResearch(
            query,
            session.access_token,
            documentId,
            3
          );

        setResults(data);

        setTimeout(() => {
          document
            .querySelector(
              ".research-results"
            )
            ?.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
        }, 150);
      } catch (error) {
        console.error(
          "Research error:",
          error
        );

        setSearchError(
          error.message ||
            "Unable to complete the research request. Please try again."
        );
      } finally {
        setLoading(false);
      }
    };


  /* =========================================================
     PDF UPLOAD
  ========================================================= */

  const handlePdfAnalysis =
    async (file) => {
      if (
        !file ||
        loading
      ) {
        return;
      }

      setShowPdfUpload(false);
      setLoading(true);
      setSearchError("");
      setUploadMessage("");

      try {
        const {
          data: { session },
          error: sessionError,
        } =
          await supabase.auth.getSession();

        if (sessionError) {
          throw sessionError;
        }

        if (
          !session?.access_token
        ) {
          navigate("/login");
          return;
        }

        const uploadResponse =
          await uploadDocument(
            file,
            session.access_token
          );

        if (
          !uploadResponse
            ?.document?.id
        ) {
          throw new Error(
            "The backend uploaded the PDF but did not return a document ID."
          );
        }

        setUploadedDocument(
          uploadResponse.document
        );

        setResults(null);
        setSearched(false);
        setQuery("");

        setUploadMessage(
          "PDF uploaded successfully! Your document has been indexed. Ask a research question about this document below."
        );

        setTimeout(() => {
          searchRef.current
            ?.scrollIntoView({
              behavior: "smooth",
              block: "center",
            });

          searchRef.current
            ?.focus();
        }, 150);
      } catch (error) {
        console.error(
          "PDF upload error:",
          error
        );

        setUploadMessage("");

        setSearchError(
          error.message ||
            "The PDF could not be uploaded. Please try again."
        );
      } finally {
        setLoading(false);
      }
    };


  /* =========================================================
     LOGOUT
  ========================================================= */

  const handleLogout =
    async () => {
      try {
        await supabase.auth.signOut();
      } catch (error) {
        console.error(
          "Logout error:",
          error
        );
      } finally {
        setProfileOpen(false);
        navigate("/");
      }
    };


  /* =========================================================
     SUGGESTIONS
  ========================================================= */

  const suggestions = [
    [
      "Artificial Intelligence",
      "Latest advances in artificial intelligence",
    ],
    [
      "Quantum Computing",
      "Recent research in quantum computing",
    ],
    [
      "Climate Change",
      "Latest scientific research about climate change",
    ],
    [
      "Machine Learning",
      "Machine learning applications in healthcare",
    ],
  ];


  /* =========================================================
     UI
  ========================================================= */

  return (
    <div
      className={`research-app-shell ${
        sidebarCollapsed
          ? "sidebar-collapsed"
          : ""
      }`}
    >

      {/* =====================================================
          SIDEBAR
      ===================================================== */}

      <aside className="research-sidebar">

        {/* COLLAPSE / EXPAND */}

        <button
          type="button"
          className="sidebar-collapse-btn"
          onClick={() =>
            setSidebarCollapsed(
              (previous) =>
                !previous
            )
          }
          title={
            sidebarCollapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
          aria-label={
            sidebarCollapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
        >
          {sidebarCollapsed
            ? "›"
            : "‹"}
        </button>


        {/* BRAND */}

        <button
          type="button"
          className="sidebar-brand"
          onClick={() =>
            navigate("/research")
          }
          title="ResoMind"
        >
          <div className="brand-mark-wrap">
            <img
              src="/resqmind-logo.jpeg"
              alt="ResoMind"
              className="brand-mark"
            />
          </div>

          <div>
            <strong>
              Reso
              <span>Mind</span>
            </strong>

            <small>
              AI Research Workspace
            </small>
          </div>
        </button>


        {/* NEW RESEARCH */}

        <button
          type="button"
          className="new-research-btn"
          onClick={focusResearch}
          title="New Research"
        >
          <Icon
            name="plus"
            size={22}
          />

          <span>
            New Research
          </span>
        </button>


        {/* MAIN NAVIGATION */}

        <nav
          className="sidebar-nav"
          aria-label="Main navigation"
        >

          <button
            type="button"
            className="active"
            onClick={focusResearch}
            title="Discover"
          >
            <Icon name="search" />

            <span>
              Discover
            </span>
          </button>


          <button
            type="button"
            onClick={() => navigate("/premium")}
            title="Research Library - Premium"
            className="premium-library-nav"
          >
             <Icon name="book" />

            <span className="premium-library-label">
            Research Library

            <small className="pro-badge">
              PRO
            </small>
             </span>
          </button>


          <button
            type="button"
            onClick={() => navigate("/research-history")}
            title="Research History"
          >
            <Icon
              name="history"
              size={18}
            />

            <span>
              Research History
            </span>
          </button>


          <button
            type="button"
            onClick={() => navigate("/saved-papers")}
            title="Saved Papers"
          >
            <Icon
              name="bookmark"
              size={18}
            />

            <span>
              Saved Papers
            </span>
          </button>

        </nav>


        {/* RESEARCH TOOLS LABEL */}

        <div className="sidebar-section-label">
          RESEARCH TOOLS
        </div>


        {/* RESEARCH TOOLS */}

        <nav
          className="sidebar-nav sidebar-tools"
          aria-label="Research tools"
        >

          <button
            type="button"
            onClick={() => {
              setSearchError("");
              setShowPdfUpload(true);
            }}
            title="Paper Analyzer"
          >
            <Icon name="file" />

            <span>
              Paper Analyzer
            </span>
          </button>


          <button
            type="button"
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
            title="Source Verification"
          >
            <Icon name="shield" />

            <span>
              Source Verification
            </span>
          </button>


          <button
            type="button"
            onClick={() => {
              if (results) {
                document
                  .querySelector(
                    ".research-results"
                  )
                  ?.scrollIntoView({
                    behavior:
                      "smooth",
                  });
              } else {
                focusResearch();
              }
            }}
            title="Research Insights"
          >
            <Icon name="chart" />

            <span>
              Research Insights
            </span>
          </button>


          <button
            type="button"
            onClick={focusResearch}
            title="AI Assistant"
          >
            <Icon name="sparkle" />

            <span>
              AI Assistant
            </span>
          </button>

        </nav>


        {/* SIDEBAR BOTTOM */}

        <div className="sidebar-bottom">

          <button
            type="button"
            className="settings-btn"
            title="Settings"
            onClick={() =>
              navigate("/settings")
            }
          >
            <Icon name="settings" />

            <span>
              Settings
            </span>
          </button>

          <div className="sidebar-ai-card">

            <div className="sidebar-ai-icon">
              <Icon
                name="sparkle"
                size={18}
              />
            </div>

            <div>
              <strong>
                ResoMind AI
              </strong>

              <span>
                Research smarter with
                intelligent AI agents.
              </span>
            </div>

          </div>

        </div>

      </aside>


      {/* =====================================================
          WORKSPACE
      ===================================================== */}

      <div className="research-workspace">

        {/* TOP BAR */}

        <header className="workspace-topbar">

          <div></div>

          <div className="topbar-actions">

            {/* ONLINE STATUS */}

            <div className="online-status">
              <span></span>
              AI systems online
            </div>


            {/* USER PROFILE */}

            <div
              className="profile-menu-wrap"
              ref={profileRef}
            >

              <button
                type="button"
                className="user-chip"
                onClick={() =>
                  setProfileOpen(
                    (previous) =>
                      !previous
                  )
                }
                aria-expanded={
                  profileOpen
                }
              >

                <div
                  className="user-avatar"
                  title={
                    currentUser?.email ||
                    "User"
                  }
                >
                  {userInitial}
                </div>


                <div className="user-meta">

                  <strong>
                    {userName ||
                      "User"}
                  </strong>

                  <span>
                    Researcher
                  </span>

                </div>


                <span
                  className={`user-chevron ${
                    profileOpen
                      ? "open"
                      : ""
                  }`}
                >
                  ⌄
                </span>

              </button>


              {/* PROFILE DROPDOWN */}

              {profileOpen && (

                <div className="profile-dropdown">

                  <div className="profile-dropdown-header">

                    <div className="profile-dropdown-avatar">
                      {userInitial}
                    </div>


                    <div>

                      <strong>
                        {userName ||
                          "User"}
                      </strong>

                      <span>
                        {currentUser
                          ?.email ||
                          ""}
                      </span>

                    </div>

                  </div>


                  <div className="profile-dropdown-divider" />


                  <button
                    type="button"
                    className="profile-logout-btn"
                    onClick={
                      handleLogout
                    }
                  >

                    <Icon
                      name="logout"
                      size={17}
                    />

                    <span>
                      Sign out
                    </span>

                  </button>

                </div>

              )}

            </div>

          </div>

        </header>


        {/* ===================================================
            MAIN CONTENT
        =================================================== */}

        <main className="workspace-content">

          {/* HERO */}

          <section className="discover-hero">

            {/* DECORATIVE BACKGROUND */}

            <div className="hero-orbit orbit-a"></div>

            <div className="hero-orbit orbit-b"></div>

            <span className="orbit-dot dot-a"></span>

            <span className="orbit-dot dot-b"></span>

            <span className="orbit-dot dot-c"></span>


            {/* HERO CONTENT */}

            <div className="hero-content-wrap">

              <div className="research-status">

                <span></span>

                AI RESEARCH PLATFORM

              </div>


              <h1>
                Research smarter.

                <br />

                <span>
                  Discover deeper.
                </span>
              </h1>


              <p className="hero-subtitle">

                Ask scientific questions,
                explore trusted research and
                let intelligent AI agents

                <br className="desktop-break" />

                retrieve evidence, analyze
                findings and verify
                information for you.

              </p>


              {/* =============================================
                  SEARCH BOX
              ============================================= */}

              <div className="research-search-box">

                <div className="research-search-icon">
                  <Icon
                    name="search"
                    size={27}
                  />
                </div>


                <textarea
                  ref={searchRef}
                  rows={1}
                  value={query}
                  placeholder={
                    uploadedDocument
                      ? "Ask a question about your uploaded PDF..."
                      : "Ask ResoMind a scientific research question..."
                  }
                  onChange={(event) => {
                    setQuery(
                      event.target.value
                    );

                    if (
                      searchError
                    ) {
                      setSearchError(
                        ""
                      );
                    }
                  }}
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

                  {/* PDF */}

                  <button
                    type="button"
                    className="search-attachment"
                    title="Upload PDF"
                    onClick={() => {
                      setSearchError(
                        ""
                      );

                      setShowPdfUpload(
                        true
                      );
                    }}
                  >
                    <Icon
                      name="paperclip"
                      size={23}
                    />
                  </button>


                  {/* SEARCH */}

                  <button
                    type="button"
                    className="research-search-button"
                    disabled={
                      !query.trim() ||
                      loading
                    }
                    onClick={
                      handleSearch
                    }
                    aria-label="Start research"
                  >

                    {loading ? (

                      <div className="button-loader"></div>

                    ) : (

                      <Icon
                        name="arrow"
                        size={25}
                      />

                    )}

                  </button>

                </div>

              </div>


              {/* =============================================
                  PDF SUCCESS
              ============================================= */}

              {uploadMessage && (

                <div className="pdf-upload-success">

                  <div className="pdf-upload-success-icon">
                    <Icon
                      name="check"
                      size={20}
                    />
                  </div>


                  <div className="pdf-upload-success-content">

                    <strong>
                      Document ready
                      for research
                    </strong>

                    <p>
                      {uploadMessage}
                    </p>

                    {uploadedDocument
                      ?.original_filename && (

                      <span className="uploaded-file-name">
                        📄{" "}
                        {
                          uploadedDocument.original_filename
                        }
                      </span>

                    )}

                  </div>

                </div>

              )}


              {/* =============================================
                  SUGGESTIONS
              ============================================= */}

              <div className="search-suggestions">

                <span>
                  Try asking:
                </span>


                {suggestions.map(
                  ([
                    label,
                    value,
                  ]) => (

                    <button
                      type="button"
                      key={label}
                      onClick={() => {
                        setQuery(
                          value
                        );

                        setTimeout(
                          () =>
                            searchRef.current
                              ?.focus(),
                          0
                        );
                      }}
                    >
                      {label}
                    </button>

                  )
                )}

              </div>


              {/* =============================================
                  QUICK TOOLS
              ============================================= */}

              <div className="quick-tools-grid">

                {/* ANALYZE PAPERS */}

                <button
                  type="button"
                  className="quick-tool-card"
                  onClick={() => {
                    setSearchError(
                      ""
                    );

                    setShowPdfUpload(
                      true
                    );
                  }}
                >

                  <div className="quick-tool-icon purple">
                    <Icon
                      name="file"
                      size={24}
                    />
                  </div>


                  <div>

                    <strong>
                      Analyze Papers
                    </strong>

                    <span>
                      Extract key insights
                      from
                      <br />
                      research papers
                    </span>

                  </div>


                  <div className="quick-arrow">
                    <Icon
                      name="arrow"
                      size={17}
                    />
                  </div>

                </button>


                {/* VERIFY SOURCES */}

                <button
                  type="button"
                  className="quick-tool-card"
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

                  <div className="quick-tool-icon green">
                    <Icon
                      name="shield"
                      size={24}
                    />
                  </div>


                  <div>

                    <strong>
                      Verify Sources
                    </strong>

                    <span>
                      Check source
                      credibility
                      <br />
                      and detect claims
                    </span>

                  </div>


                  <div className="quick-arrow">
                    <Icon
                      name="arrow"
                      size={17}
                    />
                  </div>

                </button>


                {/* RESEARCH INSIGHTS */}

                <button
                  type="button"
                  className="quick-tool-card"
                  onClick={() => {
                    if (results) {
                      document
                        .querySelector(
                          ".research-results"
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

                  <div className="quick-tool-icon blue">
                    <Icon
                      name="chart"
                      size={24}
                    />
                  </div>


                  <div>

                    <strong>
                      Research Insights
                    </strong>

                    <span>
                      Get AI-powered
                      <br />
                      research summaries
                    </span>

                  </div>


                  <div className="quick-arrow">
                    <Icon
                      name="arrow"
                      size={17}
                    />
                  </div>

                </button>


                {/* AI ASSISTANT */}

                <button
                  type="button"
                  className="quick-tool-card"
                  onClick={
                    focusResearch
                  }
                >

                  <div className="quick-tool-icon orange">
                    <Icon
                      name="bulb"
                      size={24}
                    />
                  </div>


                  <div>

                    <strong>
                      AI Assistant
                    </strong>

                    <span>
                      Explore complex
                      topics
                      <br />
                      with AI agents
                    </span>

                  </div>


                  <div className="quick-arrow">
                    <Icon
                      name="arrow"
                      size={17}
                    />
                  </div>

                </button>

              </div>


              {/* =============================================
                  TRUSTED SOURCES
              ============================================= */}

              <div className="trusted-row">

                <div className="trust-line"></div>

                <span className="trust-label">
                  Trusted by researchers
                  worldwide
                </span>

                <div className="trust-line"></div>

              </div>


              <div
                className="source-logos"
                aria-label="Research sources"
              >

                <span>
                  arXiv
                </span>

                <span>
                  PubMed
                </span>

                <span>
                  ◆ IEEE
                </span>

                <span>
                  ♞ Springer
                </span>

                <span>
                  ScienceDirect
                </span>

                <span>
                  Google Scholar
                </span>

              </div>

            </div>


            {/* =============================================
                DECORATIVE ROBOT
            ============================================= */}

            <div
              className="hero-bot"
              aria-hidden="true"
            >

              <div className="bot-antenna">
                <i></i>
              </div>


              <div className="bot-head">

                <span className="bot-eye"></span>

                <span className="bot-eye"></span>

              </div>


              <div className="bot-body">
                <Icon
                  name="sparkle"
                  size={22}
                />
              </div>


              <div className="bot-arm left"></div>

              <div className="bot-arm right"></div>

              <div className="bot-shadow"></div>

            </div>

          </section>


          {/* =================================================
              ERROR
          ================================================= */}

          {searchError && (

            <div className="research-error">

              <span>
                !
              </span>


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


          
{/* =================================================
    LOADING
================================================= */}

          {/* =================================================
              LOADING
          ================================================= */}

          {loading && (

            <section className="research-processing">

              {/* ROBOT + ANIMATED CIRCLE */}

              <div className="processing-loader">

                <div className="processing-ring">
                  <span className="orbit-dot dot-one"></span>
                  <span className="orbit-dot dot-two"></span>
                  <span className="orbit-dot dot-three"></span>
                </div>

                <div className="processing-robot-wrap">
                  <img
                    src="/loading.png"
                    alt="ResoMind AI research agents working"
                    className="processing-robot-image"
                  />
                </div>

              </div>


              {/* TEXT */}

              <h3>
                Research agents are working
              </h3>

              <p>
                Retrieving information, analyzing research
                and verifying evidence...
              </p>


              {/* PROGRESS */}

              <div className="agent-progress">

                <div className="agent-progress-track">
                  <div className="agent-progress-fill"></div>
                </div>


                <div className="agent-progress-steps">

                  <div className="agent-step retrieval-step">
                    <span className="agent-step-dot"></span>
                    <strong>Retrieval</strong>
                  </div>

                  <div className="agent-step analysis-step">
                    <span className="agent-step-dot"></span>
                    <strong>Analysis</strong>
                  </div>

                  <div className="agent-step verification-step">
                    <span className="agent-step-dot"></span>
                    <strong>Verification</strong>
                  </div>

                </div>

              </div>

            </section>

          )}

          {/* =================================================
          RESULTS
      ================================================= */}

        {searched &&
           !loading &&
        results && (

        <ResearchResults
          data={results}
          query={query}
        />

        )}

          {/* =================================================
              RESPONSIBLE AI
          ================================================= */}

          {(searched ||
            results) && (

            <div className="responsible-notice">

              <div className="notice-icon">
                <Icon
                  name="check"
                  size={18}
                />
              </div>


              <div>

                <strong>
                  Responsible AI Research
                </strong>

                <p>
                  AI-generated research
                  information should always
                  be reviewed against
                  original scientific
                  sources.
                </p>

              </div>

            </div>

          )}

        </main>

      </div>


      {/* =====================================================
          PDF MODAL
      ===================================================== */}

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