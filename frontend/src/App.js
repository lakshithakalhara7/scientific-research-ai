import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Research from "./pages/Research";
import Signup from "./pages/Signup";
import Premium from "./pages/Premium";
import Payment from "./pages/Payment";
import PaymentSuccess from "./pages/PaymentSuccess";
import PremiumLibrary from "./pages/PremiumLibrary";
import ResearchHistory from "./pages/ResearchHistory";
import SavedPapers from "./pages/SavedPapers";
import Settings from "./pages/Settings";

import ThemeManager from "./components/ThemeManager";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <ThemeManager />

      <Routes>
        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/signup"
          element={<Signup />}
        />

        <Route
          path="/research"
          element={<Research />}
        />

        <Route
          path="/premium"
          element={<Premium />}
        />

        <Route
          path="/payment"
          element={<Payment />}
        />

        <Route
          path="/payment-success"
          element={<PaymentSuccess />}
        />

        <Route
          path="/premium-library"
          element={<PremiumLibrary />}
        />

        <Route
          path="/research-history"
          element={<ResearchHistory />}
        />

        <Route
          path="/saved-papers"
          element={<SavedPapers />}
        />

        <Route
          path="/settings"
          element={<Settings />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;