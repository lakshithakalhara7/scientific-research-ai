import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../services/supabase";
import "./Signup.css";

function Signup() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const [signupNotice, setSignupNotice] = useState(null);

  const clearNotice = () => {
    if (signupNotice) {
      setSignupNotice(null);
    }
  };

  const handleGoogleSignup = () => {
    setSignupNotice({
      type: "info",
      title: "Google sign up",
      message: "Google sign up is not enabled yet.",
    });
  };

  const handleSignup = async (event) => {
    event.preventDefault();

    setSignupNotice(null);
    setLoading(true);

    try {
      const { data, error } =
        await supabase.auth.signUp({
          email: email.trim(),
          password,

          options: {
            data: {
              full_name: name.trim(),
            },
          },
        });

      if (error) {
        throw error;
      }

      /*
        If Supabase creates a session immediately,
        the account is ready and we can go directly
        to the Research workspace.
      */
      if (data.session) {
        navigate("/research");
        return;
      }

      /*
        When email confirmation is enabled Supabase
        may create the user without creating a session.
        Show the message inside our own UI instead of
        using a browser/localhost alert.
      */
      setSignupNotice({
        type: "success",
        title: "Account created",
        message:
          "Please check your email to confirm your account. After confirming, you can sign in.",
      });
    } catch (error) {
      console.error("Signup failed:", error);

      const rawMessage =
        String(error?.message || "").toLowerCase();

      if (
        rawMessage.includes("already registered") ||
        rawMessage.includes("already been registered") ||
        rawMessage.includes("user already registered")
      ) {
        setSignupNotice({
          type: "error",
          title: "Account already exists",
          message:
            "An account already exists with this email address. Try signing in instead.",
        });
      } else if (
        rawMessage.includes("password") &&
        (
          rawMessage.includes("weak") ||
          rawMessage.includes("characters") ||
          rawMessage.includes("length")
        )
      ) {
        setSignupNotice({
          type: "error",
          title: "Password not accepted",
          message:
            "Please choose a stronger password and try again.",
        });
      } else if (
        rawMessage.includes("invalid email") ||
        rawMessage.includes("email address is invalid")
      ) {
        setSignupNotice({
          type: "error",
          title: "Invalid email address",
          message:
            "Please enter a valid email address and try again.",
        });
      } else {
        setSignupNotice({
          type: "error",
          title: "Account could not be created",
          message:
            "We couldn't create your account right now. Please check your details and try again.",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-page">
      {/* Animated Background */}
      <div className="signup-background" aria-hidden="true">
        <div className="signup-grid"></div>

        <div className="signup-orb orb-one"></div>
        <div className="signup-orb orb-two"></div>
        <div className="signup-orb orb-three"></div>

        <div className="signup-beam beam-one"></div>
        <div className="signup-beam beam-two"></div>

        <div className="signup-particles">
          {Array.from({ length: 24 }).map((_, index) => (
            <span key={index}></span>
          ))}
        </div>
      </div>

      {/* Main Signup Card */}
      <main className="signup-wrapper">
        <div className="signup-card">
          {/* Logo */}
          <button
            type="button"
            className="signup-logo"
            onClick={() => navigate("/")}
            aria-label="Go home"
          >
            <div className="home-brand-logo-frame">
              <img
                src="/resqmind-logo.jpeg"
                alt="ResoMind"
                className="home-brand-logo"
              />
            </div>

            <div className="logo-copy">
              <strong>
                Reso<span>Mind</span>
              </strong>

              <small>Scientific Intelligence</small>
            </div>
          </button>

          {/* Heading */}
          <div className="signup-heading">
            <div className="signup-badge">
              <span></span>
              Join ResearchAI
            </div>

            <h1>Create your account</h1>

            <p>
              Start exploring scientific knowledge with intelligent AI.
            </p>
          </div>

          {/* Themed Status / Error Message */}
          {signupNotice && (
            <div
              className={`signup-notice signup-notice-${signupNotice.type}`}
              role={signupNotice.type === "error" ? "alert" : "status"}
              aria-live="polite"
            >
              <span
                className="signup-notice-icon"
                aria-hidden="true"
              >
                {signupNotice.type === "success"
                  ? "✓"
                  : signupNotice.type === "info"
                    ? "i"
                    : "!"}
              </span>

              <div className="signup-notice-copy">
                <strong>{signupNotice.title}</strong>
                <p>{signupNotice.message}</p>
              </div>
            </div>
          )}

          {/* Form */}
          <form className="signup-form" onSubmit={handleSignup}>
            <div className="signup-field">
              <label htmlFor="signup-name">Full Name</label>

              <div className="signup-input">
                <span className="input-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <circle
                      cx="12"
                      cy="8"
                      r="4"
                      stroke="currentColor"
                      strokeWidth="1.7"
                    />
                    <path
                      d="M4.5 20C5.3 15.8 8 14 12 14C16 14 18.7 15.8 19.5 20"
                      stroke="currentColor"
                      strokeWidth="1.7"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>

                <input
                  id="signup-name"
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(event) => {
                    setName(event.target.value);
                    clearNotice();
                  }}
                  required
                />
              </div>
            </div>

            <div className="signup-field">
              <label htmlFor="signup-email">Email address</label>

              <div className="signup-input">
                <span className="input-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <rect
                      x="3"
                      y="5"
                      width="18"
                      height="14"
                      rx="2.5"
                      stroke="currentColor"
                      strokeWidth="1.7"
                    />

                    <path
                      d="M4.5 7L12 13L19.5 7"
                      stroke="currentColor"
                      strokeWidth="1.7"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>

                <input
                  id="signup-email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(event) => {
                    setEmail(event.target.value);
                    clearNotice();
                  }}
                  required
                />
              </div>
            </div>

            <div className="signup-field">
              <label htmlFor="signup-password">Password</label>

              <div className="signup-input">
                <span className="input-icon">
                  <svg viewBox="0 0 24 24" fill="none">
                    <rect
                      x="5"
                      y="10"
                      width="14"
                      height="10"
                      rx="2"
                      stroke="currentColor"
                      strokeWidth="1.7"
                    />

                    <path
                      d="M8 10V7.5C8 5.3 9.8 3.5 12 3.5C14.2 3.5 16 5.3 16 7.5V10"
                      stroke="currentColor"
                      strokeWidth="1.7"
                      strokeLinecap="round"
                    />
                  </svg>
                </span>

                <input
                  id="signup-password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a password"
                  value={password}
                  onChange={(event) => {
                    setPassword(event.target.value);
                    clearNotice();
                  }}
                  required
                  minLength={6}
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword((current) => !current)
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="signup-submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="signup-spinner"></span>
                  Creating account...
                </>
              ) : (
                <>
                  Create Account
                  <span className="signup-arrow">→</span>
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="signup-divider">
            <span></span>
            <p>OR</p>
            <span></span>
          </div>

          {/* Google Signup */}
          <button
            type="button"
            className="signup-google"
            onClick={handleGoogleSignup}
          >
            <svg
              className="google-icon"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
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

            <span>Continue with Google</span>

            <span className="google-signup-arrow">→</span>
          </button>

          <div className="signup-login">
            <span>Already have an account?</span>

            <button
              type="button"
              onClick={() => navigate("/login")}
            >
              Sign in
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Signup;
