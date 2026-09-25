import { useNavigate } from "react-router-dom";
import "./PaymentSuccess.css";

function PaymentSuccess() {
  const navigate = useNavigate();

  return (
    <div className="payment-success-page">

      <header className="payment-success-topbar">
        <div className="payment-success-topbar-title">
          <span className="payment-success-topbar-dot" />
          Premium activated
        </div>

        <button
          type="button"
          className="payment-success-back"
          onClick={() => navigate("/premium-library")}
        >
          Go to Research Library →
        </button>
      </header>

      <main className="payment-success-content">
        <div className="payment-success-card">

          <div className="success-check success-check-animated">
            <svg
              className="success-check-svg"
              viewBox="0 0 52 52"
              aria-hidden="true"
            >
              <circle
                className="success-check-circle"
                cx="26"
                cy="26"
                r="25"
                fill="none"
              />
              <path
                className="success-check-path"
                fill="none"
                d="M14 27l7 7 17-17"
              />
            </svg>
          </div>

          <div className="success-badge">
            RESOMIND PREMIUM
          </div>

          <h1>
            Welcome to Premium!
          </h1>

          <p className="success-description">
            Your one-month Premium trial has
            been activated for this demo.
          </p>

          <div className="success-plan">
            <span>Current plan</span>

            <strong>
              Premium Researcher
            </strong>

            <small>
              1 month free
            </small>
          </div>

          <button
            type="button"
            className="success-continue-btn"
            onClick={() =>
              navigate("/premium-library")
            }
          >
            Continue to ResoMind →
          </button>

          <p className="success-note">
            Your Premium access is ready for this demo.
          </p>

        </div>
      </main>

    </div>
  );
}

export default PaymentSuccess;
