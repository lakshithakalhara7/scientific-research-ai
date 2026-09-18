import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

/* =========================================================
   SMALL SVG ICONS
========================================================= */

const AtomIcon = ({ size = 32 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 64 64"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <ellipse
      cx="32"
      cy="32"
      rx="27"
      ry="10"
      stroke="currentColor"
      strokeWidth="3"
    />
    <ellipse
      cx="32"
      cy="32"
      rx="27"
      ry="10"
      transform="rotate(60 32 32)"
      stroke="currentColor"
      strokeWidth="3"
    />
    <ellipse
      cx="32"
      cy="32"
      rx="27"
      ry="10"
      transform="rotate(120 32 32)"
      stroke="currentColor"
      strokeWidth="3"
    />
    <circle
      cx="32"
      cy="32"
      r="4.5"
      fill="currentColor"
    />
  </svg>
);

const MailIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <rect
      x="3"
      y="5"
      width="18"
      height="14"
      rx="2.5"
      stroke="currentColor"
      strokeWidth="1.8"
    />
    <path
      d="M4.5 7L12 13L19.5 7"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const LockIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <rect
      x="5"
      y="10"
      width="14"
      height="10"
      rx="2"
      stroke="currentColor"
      strokeWidth="1.8"
    />
    <path
      d="M8 10V7.5C8 5.3 9.8 3.5 12 3.5C14.2 3.5 16 5.3 16 7.5V10"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

const EyeIcon = ({ closed = false }) => (
  <svg viewBox="0 0 24 24" fill="none">
    {closed ? (
      <>
        <path
          d="M3 4L21 20"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path
          d="M10.6 10.7A2 2 0 0013.3 13.4"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path
          d="M9.2 5.4A10.7 10.7 0 0112 5C17.5 5 21 12 21 12a17 17 0 01-2.5 3.4"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path
          d="M6.2 6.3C4.1 8 3 12 3 12s3.5 7 9 7c1.1 0 2.1-.2 3-.5"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
      </>
    ) : (
      <>
        <path
          d="M3 12S6.5 5 12 5s9 7 9 7-3.5 7-9 7-9-7-9-7Z"
          stroke="currentColor"
          strokeWidth="1.8"
        />
        <circle
          cx="12"
          cy="12"
          r="2.8"
          stroke="currentColor"
          strokeWidth="1.8"
        />
      </>
    )}
  </svg>
);

const SearchIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <circle
      cx="10.5"
      cy="10.5"
      r="6"
      stroke="currentColor"
      strokeWidth="2"
    />
    <path
      d="M15 15L20 20"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);

const BrainIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <path
      d="M9.4 5.2A3.5 3.5 0 006 8.7v.3a3.2 3.2 0 00-2 3 3.2 3.2 0 002.2 3.1v.2A3.7 3.7 0 009.9 19H11V5.6a3 3 0 00-1.6-.4Z"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
    <path
      d="M14.6 5.2A3.5 3.5 0 0118 8.7v.3a3.2 3.2 0 012 3 3.2 3.2 0 01-2.2 3.1v.2a3.7 3.7 0 01-3.7 3.7H13V5.6a3 3 0 011.6-.4Z"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinejoin="round"
    />
    <path
      d="M8 10.5c1.2 0 2 .7 2 1.8M16 10.5c-1.2 0-2 .7-2 1.8"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
    />
  </svg>
);

const ShieldIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <path
      d="M12 3L19 6V11C19 15.7 16.1 19.2 12 21C7.9 19.2 5 15.7 5 11V6L12 3Z"
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

const MicroscopeIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <path
      d="M9 3H13V6H9V3Z"
      stroke="currentColor"
      strokeWidth="1.7"
    />
    <path
      d="M11 6V10.2"
      stroke="currentColor"
      strokeWidth="1.7"
    />
    <path
      d="M13.8 7.8L16.7 10.7"
      stroke="currentColor"
      strokeWidth="1.7"
    />
    <path
      d="M16.7 10.7A5 5 0 018.4 16.2"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
    />
    <path
      d="M6 19H19"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
    />
    <path
      d="M7.5 16.5H12"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
    />
  </svg>
);

const ChartIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <rect
      x="4"
      y="13"
      width="3"
      height="7"
      rx="1"
      fill="currentColor"
    />
    <rect
      x="10.5"
      y="9"
      width="3"
      height="11"
      rx="1"
      fill="currentColor"
    />
    <rect
      x="17"
      y="4"
      width="3"
      height="16"
      rx="1"
      fill="currentColor"
    />
  </svg>
);

const BookIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <path
      d="M5 5.5L11.2 4V18.5L5 20V5.5Z"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinejoin="round"
    />
    <path
      d="M19 5.5L12.8 4V18.5L19 20V5.5Z"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinejoin="round"
    />
  </svg>
);

const DnaIcon = () => (
  <svg viewBox="0 0 24 24" fill="none">
    <path
      d="M7 3C7 8 17 16 17 21"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M17 3C17 8 7 16 7 21"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M9 6H15"
      stroke="currentColor"
      strokeWidth="1.5"
    />
    <path
      d="M8 11H16"
      stroke="currentColor"
      strokeWidth="1.5"
    />
    <path
      d="M8 16H16"
      stroke="currentColor"
      strokeWidth="1.5"
    />
  </svg>
);

const GoogleLogo = () => (
  <svg width="25" height="25" viewBox="0 0 48 48">
    <path
      fill="#FFC107"
      d="M43.6 20H42V20H24V28H35.3C33.7 32.7 29.2 36 24 36C17.4 36 12 30.6 12 24C12 17.4 17.4 12 24 12C27.1 12 29.9 13.2 32 15.1L37.7 9.4C34.1 6 29.4 4 24 4C12.9 4 4 12.9 4 24C4 35.1 12.9 44 24 44C35.1 44 44 35.1 44 24C44 22.7 43.9 21.3 43.6 20Z"
    />
    <path
      fill="#FF3D00"
      d="M6.3 14.7L12.9 19.5C14.7 15.1 19 12 24 12C27.1 12 29.9 13.2 32 15.1L37.7 9.4C34.1 6 29.4 4 24 4C16.3 4 9.6 8.3 6.3 14.7Z"
    />
    <path
      fill="#4CAF50"
      d="M24 44C29.2 44 33.8 42 37.3 38.8L31.2 33.6C29.2 35.1 26.7 36 24 36C18.8 36 14.4 32.7 12.7 28.2L6.2 33.2C9.5 39.5 16.2 44 24 44Z"
    />
    <path
      fill="#1976D2"
      d="M43.6 20H42V20H24V28H35.3C34.5 30.3 33.1 32.2 31.2 33.6L37.3 38.8C36.9 39.2 44 34 44 24C44 22.7 43.9 21.3 43.6 20Z"
    />
  </svg>
);

/* =========================================================
   LOGIN COMPONENT
========================================================= */

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);

  /* =========================================================
     EMAIL LOGIN
  ========================================================= */

  const handleLogin = (event) => {
    event.preventDefault();

    setLoading(true);

    console.log("Login details:", {
      email,
      password,
      rememberMe,
    });

    // Temporary login
    setTimeout(() => {
      setLoading(false);
      navigate("/research");
    }, 1000);
  };

  /* =========================================================
     GOOGLE LOGIN
  ========================================================= */

  const handleGoogleLogin = () => {
    alert("Google Login will be connected to Firebase later.");
  };

  /* =========================================================
     FORGOT PASSWORD
  ========================================================= */

  const handleForgotPassword = () => {
    alert("Password recovery will be connected later.");
  };

  return (
    <div className="research-login-page">
      {/* =====================================================
          BACKGROUND
      ====================================================== */}

      <div className="page-background" aria-hidden="true">
        <div className="background-glow bg-glow-left"></div>
        <div className="background-glow bg-glow-center"></div>
        <div className="background-glow bg-glow-right"></div>

        <div className="shooting-line shooting-line-one"></div>
        <div className="shooting-line shooting-line-two"></div>

        <div className="page-stars">
          {Array.from({ length: 24 }).map((_, index) => (
            <span key={index}></span>
          ))}
        </div>
      </div>

      <main className="login-layout">
        {/* =====================================================
            LEFT HALF - LOGIN FORM
        ====================================================== */}

        <section className="login-left">
          <div className="login-panel">
            {/* Login Heading */}

<div className="login-heading">
  <h1>Welcome Back</h1>

  <p>
    Sign in to continue your research journey
  </p>
</div>

{/* Login Form */}

<form
  className="login-form"
  onSubmit={handleLogin}
>
              {/* Email */}

              <div className="form-field">
                <label htmlFor="email">
                  Email address
                </label>

                <div className="field-input">
                  <span className="field-icon">
                    <MailIcon />
                  </span>

                  <input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                    required
                  />
                </div>
              </div>

              {/* Password */}

              <div className="form-field">
                <label htmlFor="password">
                  Password
                </label>

                <div className="field-input">
                  <span className="field-icon">
                    <LockIcon />
                  </span>

                  <input
                    id="password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    placeholder="Enter your password"
                    value={password}
                    onChange={(event) =>
                      setPassword(event.target.value)
                    }
                    required
                  />

                  <button
                    className="show-password"
                    type="button"
                    onClick={() =>
                      setShowPassword(
                        (current) => !current
                      )
                    }
                    aria-label={
                      showPassword
                        ? "Hide password"
                        : "Show password"
                    }
                  >
                    <EyeIcon closed={showPassword} />
                  </button>
                </div>
              </div>

              {/* Options */}

              <div className="login-options">
                <label className="remember-option">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(event) =>
                      setRememberMe(
                        event.target.checked
                      )
                    }
                  />

                  <span className="checkbox-design">
                    <span>✓</span>
                  </span>

                  <span>Remember me</span>
                </label>

                <button
                  type="button"
                  className="forgot-button"
                  onClick={handleForgotPassword}
                >
                  Forgot password?
                </button>
              </div>

              {/* Sign In */}

              <button
                className="sign-in-button"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="login-spinner"></span>
                    <span>Signing In...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <span className="signin-arrow">
                      →
                    </span>
                  </>
                )}
              </button>
            </form>

            {/* Create Account */}

            <div className="create-account">
              <span>
                Don't have an account?
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/signup")
                }
              >
                Create one
              </button>
            </div>
          </div>
        </section>

        {/* =====================================================
            RIGHT HALF
            ORIGINAL ROBOT SECTION - UNCHANGED
        ====================================================== */}

        <section className="login-right">
          <div className="right-content">
            {/* Badge */}

            <div className="intelligence-badge">
              <span className="badge-dot"></span>
              <span>
                AI Research Intelligence
              </span>
            </div>

            {/* Heading */}

            <div className="right-heading">
              <h1>
                Your AI
                <br />
                <span>Research Partner</span>
              </h1>

              <p>
                Explore scientific knowledge,
                analyze research, and
                <br className="desktop-break" />
                discover meaningful insights with
                intelligent AI.
              </p>
            </div>

            {/* =================================================
                AI VISUAL
            ================================================== */}

            <div className="ai-visual">
              <div className="robot-light"></div>

              {/* Orbit Rings */}

              <div className="orbit-ring orbit-ring-one">
                <span></span>
              </div>

              <div className="orbit-ring orbit-ring-two">
                <span></span>
              </div>

              <div className="orbit-ring orbit-ring-three">
                <span></span>
              </div>

              {/* Floating Cards */}

              <div className="research-float-card float-microscope">
                <MicroscopeIcon />
              </div>

              <div className="research-float-card float-chart">
                <ChartIcon />
              </div>

              <div className="research-float-card float-dna">
                <DnaIcon />
              </div>

              <div className="research-float-card float-books">
                <BookIcon />
              </div>

              {/* =================================================
                  ROBOT
              ================================================== */}

              <div className="robot-wrapper">
                <div className="robot">
                  {/* Robot Ears */}

                  <div className="robot-ear robot-ear-left"></div>
                  <div className="robot-ear robot-ear-right"></div>

                  {/* Robot Head */}

                  <div className="robot-head">
                    <div className="robot-screen">
                      <div className="robot-eye robot-eye-left"></div>
                      <div className="robot-eye robot-eye-right"></div>
                    </div>
                  </div>

                  {/* Robot Neck */}

                  <div className="robot-neck"></div>

                  {/* Robot Body */}

                  <div className="robot-body">
                    <div className="robot-body-core">
                      <AtomIcon size={42} />
                    </div>
                  </div>

                  {/* Left Arm */}

                  <div className="robot-arm robot-arm-left">
                    <div className="robot-hand">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>

                  {/* Right Arm */}

                  <div className="robot-arm robot-arm-right"></div>

                  {/* Legs */}

                  <div className="robot-leg robot-leg-left"></div>
                  <div className="robot-leg robot-leg-right"></div>
                </div>
              </div>

              {/* Platform */}

              <div className="robot-platform">
                <div className="platform-inner"></div>
                <div className="platform-center"></div>
              </div>
            </div>

            {/* =================================================
                FEATURES
            ================================================== */}

            <div className="right-features">
              {/* Smart Search */}

              <div className="right-feature">
                <div className="feature-icon search-feature">
                  <SearchIcon />
                </div>

                <div className="feature-copy">
                  <strong>Smart Search</strong>

                  <span>
                    Find relevant research
                    <br />
                    instantly.
                  </span>
                </div>
              </div>

              {/* AI Analysis */}

              <div className="right-feature">
                <div className="feature-icon brain-feature">
                  <BrainIcon />
                </div>

                <div className="feature-copy">
                  <strong>AI Analysis</strong>

                  <span>
                    Understand complex
                    <br />
                    research.
                  </span>
                </div>
              </div>

              {/* Verification */}

              <div className="right-feature">
                <div className="feature-icon shield-feature">
                  <ShieldIcon />
                </div>

                <div className="feature-copy">
                  <strong>Verification</strong>

                  <span>
                    Check trusted scientific
                    <br />
                    sources.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Login;