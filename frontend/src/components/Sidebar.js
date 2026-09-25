import { useLocation, useNavigate } from "react-router-dom";
import "./Sidebar.css";

function SidebarIcon({ name, size = 20 }) {
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
        <circle cx="11" cy="11" r="7" />
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
    bookmark: <path d="M6 4.5A1.5 1.5 0 0 1 7.5 3h9A1.5 1.5 0 0 1 18 4.5V21l-6-4-6 4z" />,
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
    lock: (
      <>
        <rect x="6.5" y="10" width="11" height="9" rx="2" />
        <path d="M9 10V7.5a3 3 0 0 1 6 0V10" />
      </>
    ),
    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21h-4v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3.1 14H3v-4h.1A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3.1V3h4v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.5 1H21v4h-.1a1.7 1.7 0 0 0-1.5 1z" />
      </>
    ),
  };

  return <svg {...common}>{paths[name]}</svg>;
}

function Sidebar({
  collapsed = false,
  onToggle,
  activePage,
  onNewResearch,
  onPaperAnalyzer,
  onSourceVerification,
  onResearchInsights,
  onAIAssistant,
  publicMode = false,
}) {
  const navigate = useNavigate();
  const location = useLocation();

  const currentPage =
    activePage ||
    (location.pathname === "/research"
      ? "discover"
      : location.pathname === "/premium"
        ? "library"
        : location.pathname === "/research-history"
          ? "history"
          : location.pathname === "/saved-papers"
            ? "saved"
            : location.pathname === "/settings"
              ? "settings"
              : "");

  const runOrNavigate = (callback, path) => {
    if (callback) {
      callback();
      return;
    }
    navigate(path);
  };

  const sendToLogin = (returnTo) => {
    navigate("/login", {
      state: {
        returnTo,
        message: "Please sign in to access this feature.",
      },
    });
  };

  const runProtected = (callback, path) => {
    if (publicMode) {
      sendToLogin(path);
      return;
    }

    runOrNavigate(callback, path);
  };

  const protectedClass = publicMode
    ? "sidebar-public-protected"
    : "";

  const protectedTitle = (label) =>
    publicMode ? `${label} - Sign in required` : label;

  return (
    <aside className="research-sidebar">
      <button
        type="button"
        className="sidebar-collapse-btn"
        onClick={onToggle}
        title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? "›" : "‹"}
      </button>

      <button
        type="button"
        className="sidebar-brand"
        onClick={() => navigate(publicMode ? "/" : "/research")}
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
            Reso<span>Mind</span>
          </strong>
          <small>AI Research Workspace</small>
        </div>
      </button>

      <button
        type="button"
        className="new-research-btn"
        onClick={() => runOrNavigate(onNewResearch, publicMode ? "/" : "/research")}
        title="New Research"
      >
        <SidebarIcon name="plus" size={22} />
        <span>New Research</span>
      </button>

      <nav className="sidebar-nav" aria-label="Main navigation">
        <button
          type="button"
          className={currentPage === "discover" ? "active" : ""}
          aria-current={currentPage === "discover" ? "page" : undefined}
          onClick={() => runOrNavigate(onNewResearch, publicMode ? "/" : "/research")}
          title="Discover"
        >
          <SidebarIcon name="search" />
          <span>Discover</span>
        </button>

        <button
          type="button"
          onClick={() => runProtected(null, "/premium")}
          title={protectedTitle("Research Library - Premium")}
          className={`premium-library-nav ${protectedClass} ${currentPage === "library" ? "active" : ""}`}
          aria-current={currentPage === "library" ? "page" : undefined}
        >
          <SidebarIcon name="book" />
          <span className="premium-library-label">
            Research Library
            <small className="pro-badge">PRO</small>
          </span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>

        <button
          type="button"
          className={`${protectedClass} ${currentPage === "history" ? "active" : ""}`}
          aria-current={currentPage === "history" ? "page" : undefined}
          onClick={() => runProtected(null, "/research-history")}
          title={protectedTitle("Research History")}
        >
          <SidebarIcon name="history" size={18} />
          <span>Research History</span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>

        <button
          type="button"
          className={`${protectedClass} ${currentPage === "saved" ? "active" : ""}`}
          aria-current={currentPage === "saved" ? "page" : undefined}
          onClick={() => runProtected(null, "/saved-papers")}
          title={protectedTitle("Saved Papers")}
        >
          <SidebarIcon name="bookmark" size={18} />
          <span>Saved Papers</span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>
      </nav>

      <div className="sidebar-section-label">RESEARCH TOOLS</div>

      <nav className="sidebar-nav sidebar-tools" aria-label="Research tools">
        <button
          type="button"
          onClick={() => runProtected(onPaperAnalyzer, "/research")}
          title={protectedTitle("Paper Analyzer")}
          className={protectedClass}
        >
          <SidebarIcon name="file" />
          <span>Paper Analyzer</span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>

        <button
          type="button"
          onClick={() => runProtected(onSourceVerification, "/research")}
          title={protectedTitle("Source Verification")}
          className={protectedClass}
        >
          <SidebarIcon name="shield" />
          <span>Source Verification</span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>

        <button
          type="button"
          onClick={() => runProtected(onResearchInsights, "/research")}
          title={protectedTitle("Research Insights")}
          className={protectedClass}
        >
          <SidebarIcon name="chart" />
          <span>Research Insights</span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>

        <button
          type="button"
          onClick={() => runProtected(onAIAssistant, "/research")}
          title={protectedTitle("AI Assistant")}
          className={protectedClass}
        >
          <SidebarIcon name="sparkle" />
          <span>AI Assistant</span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>
      </nav>

      <div className="sidebar-bottom">
        <button
          type="button"
          className={`settings-btn ${protectedClass} ${currentPage === "settings" ? "active" : ""}`}
          aria-current={currentPage === "settings" ? "page" : undefined}
          title={protectedTitle("Settings")}
          onClick={() => runProtected(null, "/settings")}
        >
          <SidebarIcon name="settings" />
          <span>Settings</span>
          {publicMode && (
            <small className="sidebar-lock-indicator" aria-hidden="true">
              <SidebarIcon name="lock" size={13} />
            </small>
          )}
        </button>

        <div className="sidebar-ai-card">
          <div className="sidebar-ai-icon">
            <SidebarIcon name="sparkle" size={18} />
          </div>
          <div>
            <strong>ResoMind AI</strong>
            <span>Research smarter with intelligent AI agents.</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
