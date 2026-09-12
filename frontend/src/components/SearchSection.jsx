import React from 'react';

const EXAMPLE_QUERIES = [
  "Is coffee bad for your heart?",
  "Did the US pass the new privacy bill?",
  "Do electric vehicles produce more lifetime emissions?",
];

export default function SearchSection({ claim, setClaim, onVerify, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (claim.trim() && !isLoading) {
      onVerify(claim.trim());
    }
  };

  const handleChipClick = (query) => {
    setClaim(query);
    if (!isLoading) {
      onVerify(query);
    }
  };

  return (
    <section id="home-view" className="view-section">
      <div className="hero-container">
        <h1 className="hero-brand">Tathvyn</h1>
        <p className="tagline">Clear answers, verified facts.</p>
      </div>

      <form id="search-form" className="search-container" onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            id="claim-input"
            placeholder="What claim do you want to verify?"
            required
            autoComplete="off"
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" id="search-submit" aria-label="Verify" disabled={!claim.trim() || isLoading}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </button>
        </div>
      </form>

      <div className="example-queries">
        <span className="example-label">Try asking:</span>
        {EXAMPLE_QUERIES.map((q, idx) => (
          <button
            key={idx}
            type="button"
            className="example-chip"
            onClick={() => handleChipClick(q)}
            disabled={isLoading}
          >
            {q}
          </button>
        ))}
      </div>
    </section>
  );
}
