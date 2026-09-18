function Loading({ message }) {
  return (
    <div className="modern-loading">
      <div className="loading-animation">
        <span></span>
        <span></span>
        <span></span>
      </div>

      <h3>Research agents are working</h3>

      <p>
        {message ||
          "Retrieving papers, analyzing evidence, and verifying sources..."}
      </p>

      <div className="agent-status">
        <span>Retrieval</span>
        <span>Analysis</span>
        <span>Verification</span>
      </div>
    </div>
  );
}

export default Loading;