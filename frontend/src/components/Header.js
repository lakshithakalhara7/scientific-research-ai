function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h1>ResearchAI</h1>
            <span>Scientific Intelligence Platform</span>
          </div>
        </div>

        <nav className="nav">
          <a href="#research">Research</a>
          <a href="#papers">Papers</a>
          <a href="#analysis">Analysis</a>
          <a href="#verification">Verification</a>
        </nav>

        <div className="status">
          <span className="status-dot"></span>
          AI System Online
        </div>
      </div>
    </header>
  );
}

export default Header;