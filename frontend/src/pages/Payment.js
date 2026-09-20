import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Payment.css";

function Payment() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    cardholderName: "",
    cardNumber: "",
    expiry: "",
    cvc: "",
    country: "",
  });

  const [errors, setErrors] = useState({});
  const [processing, setProcessing] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    let formattedValue = value;

    /* Card number formatting */
    if (name === "cardNumber") {
      const numbersOnly = value
        .replace(/\D/g, "")
        .slice(0, 16);

      formattedValue =
        numbersOnly
          .replace(/(.{4})/g, "$1 ")
          .trim();
    }

    /* Expiry formatting MM/YY */
    if (name === "expiry") {
      const numbersOnly = value
        .replace(/\D/g, "")
        .slice(0, 4);

      if (numbersOnly.length > 2) {
        formattedValue =
          `${numbersOnly.slice(0, 2)}/${numbersOnly.slice(2)}`;
      } else {
        formattedValue = numbersOnly;
      }
    }

    /* CVC formatting */
    if (name === "cvc") {
      formattedValue =
        value
          .replace(/\D/g, "")
          .slice(0, 3);
    }

    setForm((previous) => ({
      ...previous,
      [name]: formattedValue,
    }));

    setErrors((previous) => ({
      ...previous,
      [name]: "",
    }));
  };

  const validateForm = () => {
    const nextErrors = {};

    if (!form.cardholderName.trim()) {
      nextErrors.cardholderName =
        "Cardholder name is required.";
    }

    const cardDigits =
      form.cardNumber.replace(/\s/g, "");

    if (cardDigits.length !== 16) {
      nextErrors.cardNumber =
        "Enter a 16-digit demo card number.";
    }

    if (!/^\d{2}\/\d{2}$/.test(form.expiry)) {
      nextErrors.expiry =
        "Enter expiry as MM/YY.";
    } else {
      const month =
        Number(form.expiry.slice(0, 2));

      if (month < 1 || month > 12) {
        nextErrors.expiry =
          "Enter a valid expiry month.";
      }
    }

    if (!/^\d{3}$/.test(form.cvc)) {
      nextErrors.cvc =
        "Enter a 3-digit demo CVC.";
    }

    if (!form.country) {
      nextErrors.country =
        "Please select your country.";
    }

    setErrors(nextErrors);

    return (
      Object.keys(nextErrors).length === 0
    );
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    setProcessing(true);

    /*
      DEMO CHECKOUT ONLY.

      We intentionally do NOT send or store
      cardNumber, expiry, or CVC.

      In Step 5 we will activate Premium using
      safe subscription data instead.
    */

    setTimeout(() => {
      setProcessing(false);

      navigate("/payment-success");
    }, 1200);
  };

  return (
    <div className="payment-page">

      {/* =====================================
          HEADER
      ====================================== */}

      <header className="payment-header">

        <button
          type="button"
          className="payment-back"
          onClick={() => navigate("/premium")}
        >
          ← Back
        </button>

        <div className="payment-logo">
          Reso<span>Mind</span>
        </div>

        <div className="secure-label">
          🔒 Secure checkout
        </div>

      </header>


      {/* =====================================
          MAIN
      ====================================== */}

      <main className="payment-container">

        {/* LEFT SIDE */}

        <section className="checkout-section">

          <div className="checkout-badge">
            ✦ RESOMIND PREMIUM
          </div>

          <h1>
            Start your
            <span> free month</span>
          </h1>

          <p className="checkout-description">
            Enter demo payment details to continue.
            You will not be charged today.
          </p>


          {/* DEMO WARNING */}

          <div className="demo-payment-notice">
            <span>ⓘ</span>

            <div>
              <strong>
                Demo checkout
              </strong>

              <p>
                Do not enter a real card number.
                This university project does not
                process or store payment card data.
              </p>
            </div>
          </div>


          {/* =================================
              PAYMENT FORM
          ================================== */}

          <form
            className="payment-form"
            onSubmit={handleSubmit}
          >

            <div className="form-section-title">
              Payment details
            </div>


            {/* NAME */}

            <div className="payment-field">

              <label htmlFor="cardholderName">
                Cardholder name
              </label>

              <input
                id="cardholderName"
                name="cardholderName"
                type="text"
                value={form.cardholderName}
                onChange={handleChange}
                placeholder="Demo User"
                autoComplete="off"
              />

              {errors.cardholderName && (
                <span className="field-error">
                  {errors.cardholderName}
                </span>
              )}

            </div>


            {/* CARD NUMBER */}

            <div className="payment-field">

              <label htmlFor="cardNumber">
                Card number
              </label>

              <div className="card-input-wrap">

                <input
                  id="cardNumber"
                  name="cardNumber"
                  type="text"
                  inputMode="numeric"
                  value={form.cardNumber}
                  onChange={handleChange}
                  placeholder="4242 4242 4242 4242"
                  maxLength={19}
                  autoComplete="off"
                />

                <span className="card-icon">
                  💳
                </span>

              </div>

              {errors.cardNumber && (
                <span className="field-error">
                  {errors.cardNumber}
                </span>
              )}

            </div>


            {/* EXPIRY + CVC */}

            <div className="payment-field-row">

              <div className="payment-field">

                <label htmlFor="expiry">
                  Expiry
                </label>

                <input
                  id="expiry"
                  name="expiry"
                  type="text"
                  inputMode="numeric"
                  value={form.expiry}
                  onChange={handleChange}
                  placeholder="MM/YY"
                  maxLength={5}
                  autoComplete="off"
                />

                {errors.expiry && (
                  <span className="field-error">
                    {errors.expiry}
                  </span>
                )}

              </div>


              <div className="payment-field">

                <label htmlFor="cvc">
                  CVC
                </label>

                <input
                  id="cvc"
                  name="cvc"
                  type="password"
                  inputMode="numeric"
                  value={form.cvc}
                  onChange={handleChange}
                  placeholder="123"
                  maxLength={3}
                  autoComplete="off"
                />

                {errors.cvc && (
                  <span className="field-error">
                    {errors.cvc}
                  </span>
                )}

              </div>

            </div>


            {/* COUNTRY */}

            <div className="payment-field">

              <label htmlFor="country">
                Country / Region
              </label>

              <select
                id="country"
                name="country"
                value={form.country}
                onChange={handleChange}
              >

                <option value="">
                  Select country
                </option>

                <option value="Sri Lanka">
                  Sri Lanka
                </option>

                <option value="India">
                  India
                </option>

                <option value="United Kingdom">
                  United Kingdom
                </option>

                <option value="United States">
                  United States
                </option>

                <option value="Australia">
                  Australia
                </option>

                <option value="Other">
                  Other
                </option>

              </select>

              {errors.country && (
                <span className="field-error">
                  {errors.country}
                </span>
              )}

            </div>


            {/* SUBMIT */}

            <button
              type="submit"
              className="checkout-button"
              disabled={processing}
            >
              {processing
                ? "Activating..."
                : "Start Free Month →"}
            </button>


            <p className="checkout-security">
              🔒 Demo checkout — no real payment
              information is transmitted or stored.
            </p>

          </form>

        </section>


        {/* =====================================
            ORDER SUMMARY
        ====================================== */}

        <aside className="order-summary">

          <div className="summary-top">

            <span className="summary-plan-label">
              YOUR PLAN
            </span>

            <h2>
              Premium Researcher
            </h2>

            <p>
              Full access to ResoMind's
              Premium Research Library.
            </p>

          </div>


          <div className="summary-divider" />


          <div className="summary-feature">
            <span>✓</span>
            Research PDF Library
          </div>

          <div className="summary-feature">
            <span>✓</span>
            Research Categories
          </div>

          <div className="summary-feature">
            <span>✓</span>
            AI Paper Analysis
          </div>

          <div className="summary-feature">
            <span>✓</span>
            Source Verification
          </div>

          <div className="summary-feature">
            <span>✓</span>
            Advanced Search
          </div>


          <div className="summary-divider" />


          <div className="price-row">

            <span>
              First month
            </span>

            <strong className="free-price">
              FREE
            </strong>

          </div>


          <div className="price-row muted">

            <span>
              After trial
            </span>

            <span>
              $4.99 / month
            </span>

          </div>


          <div className="summary-total">

            <div>
              <span>
                Due today
              </span>

              <small>
                1-month free offer
              </small>
            </div>

            <strong>
              $0.00
            </strong>

          </div>


          <div className="cancel-note">
            <span>✓</span>

            <p>
              Cancel anytime before the end
              of your free month.
            </p>
          </div>

        </aside>

      </main>

    </div>
  );
}

export default Payment;