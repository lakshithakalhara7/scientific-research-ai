import {
  useEffect,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  supabase,
} from "../services/supabase";

import DashboardLayout from "../components/DashboardLayout";

import "./Settings.css";


function Settings() {

  const navigate = useNavigate();


  /* =======================================================
     USER
  ======================================================= */

  const [user, setUser] =
    useState(null);

  const [fullName, setFullName] =
    useState("");

  const [email, setEmail] =
    useState("");


  /* =======================================================
     APPEARANCE
  ======================================================= */

  const [theme, setTheme] =
    useState(
      () =>
        localStorage.getItem(
          "resomind_theme"
        ) || "light"
    );


  /* =======================================================
     RESEARCH SETTINGS
  ======================================================= */

  const [verificationEnabled, setVerificationEnabled] =
    useState(
      () =>
        localStorage.getItem(
          "resomind_verification"
        ) !== "false"
    );

  const [researchNotifications, setResearchNotifications] =
    useState(
      () =>
        localStorage.getItem(
          "resomind_research_notifications"
        ) !== "false"
    );

  const [sourceNotifications, setSourceNotifications] =
    useState(
      () =>
        localStorage.getItem(
          "resomind_source_notifications"
        ) !== "false"
    );

  const [defaultResults, setDefaultResults] =
    useState(
      () =>
        localStorage.getItem(
          "resomind_default_results"
        ) || "3"
    );


  /* =======================================================
     SAVE MESSAGE
  ======================================================= */

  const [message, setMessage] =
    useState("");


  /* =======================================================
     LOAD AUTHENTICATED USER
  ======================================================= */

  useEffect(() => {

    const loadUser = async () => {

      const {
        data,
      } =
        await supabase.auth.getUser();


      if (!data?.user) {
        return;
      }


      setUser(
        data.user
      );


      setEmail(
        data.user.email || ""
      );


      const metadata =
        data.user.user_metadata || {};


      setFullName(
        metadata.full_name ||
        metadata.name ||
        data.user.email
          ?.split("@")[0] ||
        ""
      );

    };


    loadUser();

  }, []);


  /* =======================================================
     APPLY THEME
  ======================================================= */

  useEffect(() => {

    const root =
      document.documentElement;


    const applyTheme = () => {

      let activeTheme =
        theme;


      if (theme === "system") {

        const prefersDark =
          window.matchMedia(
            "(prefers-color-scheme: dark)"
          ).matches;


        activeTheme =
          prefersDark
            ? "dark"
            : "light";

      }


      root.setAttribute(
        "data-resomind-theme",
        activeTheme
      );

    };


    applyTheme();


    const media =
      window.matchMedia(
        "(prefers-color-scheme: dark)"
      );


    const handleSystemChange =
      () => {

        if (theme === "system") {
          applyTheme();
        }

      };


    media.addEventListener(
      "change",
      handleSystemChange
    );


    return () => {

      media.removeEventListener(
        "change",
        handleSystemChange
      );

    };

  }, [theme]);


  /* =======================================================
     CHANGE THEME
  ======================================================= */

  const handleThemeChange = (
    selectedTheme
  ) => {

    setTheme(
      selectedTheme
    );


    localStorage.setItem(
      "resomind_theme",
      selectedTheme
    );

  };


  /* =======================================================
     SAVE SETTINGS
  ======================================================= */

  const handleSave = async () => {

    try {

      localStorage.setItem(
        "resomind_verification",
        String(
          verificationEnabled
        )
      );


      localStorage.setItem(
        "resomind_research_notifications",
        String(
          researchNotifications
        )
      );


      localStorage.setItem(
        "resomind_source_notifications",
        String(
          sourceNotifications
        )
      );


      localStorage.setItem(
        "resomind_default_results",
        defaultResults
      );


      /*
       * Update Supabase profile metadata.
       */

      if (user) {

        const {
          error,
        } =
          await supabase.auth.updateUser({
            data: {
              full_name:
                fullName.trim(),
            },
          });


        if (error) {
          throw error;
        }

      }


      setMessage(
        "Settings saved successfully."
      );


      setTimeout(
        () => setMessage(""),
        3000
      );

    } catch (error) {

      console.error(
        "Settings save error:",
        error
      );


      setMessage(
        "Unable to save settings."
      );

    }

  };


  /* =======================================================
     LOGOUT
  ======================================================= */

  const handleLogout = async () => {

    await supabase.auth.signOut();

    navigate("/");

  };


  /* =======================================================
     INITIAL
  ======================================================= */

  const initial =
    fullName
      ? fullName
          .charAt(0)
          .toUpperCase()
      : "R";


  return (

    <DashboardLayout activePage="settings">
      <div className="settings-page">


      {/* =================================================
          WORKSPACE
      ================================================= */}

      <div className="settings-workspace">


        {/* TOP BAR */}

        <header className="settings-topbar">

          <div className="settings-online">

            <span></span>

            AI systems online

          </div>


          <button
            type="button"
            className="settings-back"
            onClick={() =>
              navigate("/research")
            }
          >

            Back to Research

            <span>→</span>

          </button>

        </header>


        {/* =================================================
            MAIN CONTENT
        ================================================= */}

        <main className="settings-content">


          {/* PAGE HEADER */}

          <section className="settings-header">

            <div className="settings-header-icon">

              ⚙

            </div>


            <div>

              <span className="settings-eyebrow">

                PREFERENCES

              </span>


              <h1>

                Settings

              </h1>


              <p>

                Manage your ResoMind profile,
                appearance, research preferences
                and account settings.

              </p>

            </div>

          </section>


          {/* =================================================
              PROFILE
          ================================================= */}

          <section className="settings-panel">

            <div className="settings-panel-heading">

              <div>

                <span className="settings-section-icon">

                  ♙

                </span>


                <div>

                  <h2>
                    Profile
                  </h2>

                  <p>
                    Manage your personal
                    researcher information.
                  </p>

                </div>

              </div>

            </div>


            <div className="settings-profile">


              <div className="settings-large-avatar">

                {initial}

              </div>


              <div className="settings-profile-details">

                <strong>

                  {fullName ||
                    "Researcher"}

                </strong>

                <span>

                  Researcher

                </span>

                <small>

                  {email ||
                    "Loading account..."}

                </small>

              </div>

            </div>


            <div className="settings-form-grid">


              <div className="settings-field">

                <label>
                  Display name
                </label>

                <input
                  type="text"
                  value={fullName}
                  onChange={(event) =>
                    setFullName(
                      event.target.value
                    )
                  }
                  placeholder="Your name"
                />

              </div>


              <div className="settings-field">

                <label>
                  Email address
                </label>

                <input
                  type="email"
                  value={email}
                  disabled
                />

                <small>
                  Email is linked to your
                  ResoMind account.
                </small>

              </div>

            </div>

          </section>


          {/* =================================================
              APPEARANCE
          ================================================= */}

          <section className="settings-panel">

            <div className="settings-panel-heading">

              <div>

                <span className="settings-section-icon">

                  ◐

                </span>


                <div>

                  <h2>
                    Appearance
                  </h2>

                  <p>
                    Choose how ResoMind looks
                    on this device.
                  </p>

                </div>

              </div>

            </div>


            <div className="theme-options">


              <button
                type="button"
                className={
                  theme === "light"
                    ? "theme-option active"
                    : "theme-option"
                }
                onClick={() =>
                  handleThemeChange(
                    "light"
                  )
                }
              >

                <div className="theme-preview light-preview">

                  <span></span>

                  <i></i>

                  <i></i>

                </div>


                <div>

                  <strong>
                    ☀ Light
                  </strong>

                  <span>
                    Bright research workspace
                  </span>

                </div>

              </button>


              <button
                type="button"
                className={
                  theme === "dark"
                    ? "theme-option active"
                    : "theme-option"
                }
                onClick={() =>
                  handleThemeChange(
                    "dark"
                  )
                }
              >

                <div className="theme-preview dark-preview">

                  <span></span>

                  <i></i>

                  <i></i>

                </div>


                <div>

                  <strong>
                    ☾ Dark
                  </strong>

                  <span>
                    Comfortable low-light view
                  </span>

                </div>

              </button>


              <button
                type="button"
                className={
                  theme === "system"
                    ? "theme-option active"
                    : "theme-option"
                }
                onClick={() =>
                  handleThemeChange(
                    "system"
                  )
                }
              >

                <div className="theme-preview system-preview">

                  <span></span>

                  <i></i>

                  <i></i>

                </div>


                <div>

                  <strong>
                    ◐ System
                  </strong>

                  <span>
                    Follow your device theme
                  </span>

                </div>

              </button>

            </div>

          </section>


          {/* =================================================
              RESEARCH PREFERENCES
          ================================================= */}

          <section className="settings-panel">

            <div className="settings-panel-heading">

              <div>

                <span className="settings-section-icon">

                  ✦

                </span>


                <div>

                  <h2>
                    Research Preferences
                  </h2>

                  <p>
                    Configure your AI research
                    workflow.
                  </p>

                </div>

              </div>

            </div>


            <div className="settings-preference-row">

              <div>

                <strong>
                  Source verification
                </strong>

                <span>
                  Verify AI-generated claims
                  against retrieved research
                  sources.
                </span>

              </div>


              <button
                type="button"
                aria-label="Toggle source verification"
                className={
                  verificationEnabled
                    ? "settings-switch active"
                    : "settings-switch"
                }
                onClick={() =>
                  setVerificationEnabled(
                    (previous) =>
                      !previous
                  )
                }
              >

                <span></span>

              </button>

            </div>


            <div className="settings-preference-row">

              <div>

                <strong>
                  Default retrieval results
                </strong>

                <span>
                  Choose the default number of
                  document chunks used for
                  research.
                </span>

              </div>


              <select
                className="settings-select"
                value={defaultResults}
                onChange={(event) =>
                  setDefaultResults(
                    event.target.value
                  )
                }
              >

                <option value="3">
                  3 results
                </option>

                <option value="5">
                  5 results
                </option>

                <option value="10">
                  10 results
                </option>

              </select>

            </div>

          </section>


          {/* =================================================
              NOTIFICATIONS
          ================================================= */}

          <section className="settings-panel">

            <div className="settings-panel-heading">

              <div>

                <span className="settings-section-icon">

                  ♢

                </span>


                <div>

                  <h2>
                    Notifications
                  </h2>

                  <p>
                    Control research status
                    notifications.
                  </p>

                </div>

              </div>

            </div>


            <div className="settings-preference-row">

              <div>

                <strong>
                  Research completed
                </strong>

                <span>
                  Show a notification when
                  AI research processing
                  finishes.
                </span>

              </div>


              <button
                type="button"
                aria-label="Toggle research notifications"
                className={
                  researchNotifications
                    ? "settings-switch active"
                    : "settings-switch"
                }
                onClick={() =>
                  setResearchNotifications(
                    (previous) =>
                      !previous
                  )
                }
              >

                <span></span>

              </button>

            </div>


            <div className="settings-preference-row">

              <div>

                <strong>
                  Verification alerts
                </strong>

                <span>
                  Alert when research contains
                  partially supported or
                  conflicting claims.
                </span>

              </div>


              <button
                type="button"
                aria-label="Toggle verification alerts"
                className={
                  sourceNotifications
                    ? "settings-switch active"
                    : "settings-switch"
                }
                onClick={() =>
                  setSourceNotifications(
                    (previous) =>
                      !previous
                  )
                }
              >

                <span></span>

              </button>

            </div>

          </section>


          {/* =================================================
              SECURITY
          ================================================= */}

          <section className="settings-panel">

            <div className="settings-panel-heading">

              <div>

                <span className="settings-section-icon">

                  ♢

                </span>


                <div>

                  <h2>
                    Privacy & Security
                  </h2>

                  <p>
                    Information about your
                    authenticated research
                    workspace.
                  </p>

                </div>

              </div>

            </div>


            <div className="settings-security-card">

              <div className="security-icon">

                ✓

              </div>


              <div>

                <strong>
                  Authenticated session
                </strong>

                <span>
                  Your ResoMind workspace is
                  connected to your signed-in
                  account.
                </span>

              </div>

            </div>

          </section>


          {/* =================================================
              ACCOUNT
          ================================================= */}

          <section className="settings-panel">

            <div className="settings-panel-heading">

              <div>

                <span className="settings-section-icon">

                  ◇

                </span>


                <div>

                  <h2>
                    Account
                  </h2>

                  <p>
                    Manage your current
                    ResoMind session.
                  </p>

                </div>

              </div>

            </div>


            <div className="settings-account-row">

              <div>

                <strong>
                  Sign out
                </strong>

                <span>
                  Sign out from this
                  ResoMind account.
                </span>

              </div>


              <button
                type="button"
                className="settings-logout-btn"
                onClick={
                  handleLogout
                }
              >

                Sign Out

              </button>

            </div>

          </section>


          {/* =================================================
              SAVE
          ================================================= */}

          <div className="settings-save-area">


            {message && (

              <span className="settings-message">

                ✓ {message}

              </span>

            )}


            <button
              type="button"
              className="settings-save-btn"
              onClick={
                handleSave
              }
            >

              Save Changes

            </button>

          </div>


        </main>

        </div>

      </div>
    </DashboardLayout>

  );

}

export default Settings;