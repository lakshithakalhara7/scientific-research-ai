import { useNavigate } from "react-router-dom";
import "./PaymentSuccess.css";

function PaymentSuccess() {
  const navigate = useNavigate();

  return (
    <div className="payment-success-page">

      <div className="payment-success-card">

        <div className="success-check">
          ✓
        </div>

        <div className="success-badge">
          RESOMIND PREMIUM
        </div>

        <h1>
          Welcome to Premium!
        </h1>

        <p>
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
          onClick={() =>
            navigate("/premium-library")
          }
        >
          Continue to ResoMind →
        </button>

        <p className="success-note">
          Next we'll connect this to your
          actual Premium account status.
        </p>

      </div>

    </div>
  );
}

export default PaymentSuccess;