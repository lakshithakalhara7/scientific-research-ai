function SearchBox({ query, setQuery, onSearch, loading }) {
  return (
    <section className="hero-search" id="research">
      <div className="search-label">
        <span className="search-icon">⌕</span>
        Research Assistant
      </div>

      <textarea
        className="modern-input"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Ask anything about scientific research..."
        disabled={loading}
      />

      <div className="search-bottom">
        <span className="search-tip">
          Try: "What are the latest applications of AI in medical imaging?"
        </span>

        <button
          className="search-button"
          onClick={onSearch}
          disabled={loading || !query.trim()}
        >
          {loading ? (
            <>
              <span className="button-spinner"></span>
              Processing
            </>
          ) : (
            <>
              Search Research
              <span>→</span>
            </>
          )}
        </button>
      </div>
    </section>
  );
}

export default SearchBox;