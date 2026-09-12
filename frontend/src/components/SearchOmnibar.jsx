import React from 'react';
import { ArrowUp, Zap, Sparkles } from 'lucide-react';

const EXAMPLE_CLAIMS = [
  "James Webb Space Telescope discovered traces of dimethyl sulfide on K2-18b",
  "India landed Chandrayaan-3 on the lunar south pole region in 2023",
  "Quantum computers have broken standard RSA-2048 encryption",
  "Coffee consumption reduces all-cause mortality risk by 15%",
];

export default function SearchOmnibar({
  claim,
  setClaim,
  depth,
  setDepth,
  onSubmit,
  isLoading,
  compact,
}) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (claim.trim() && !isLoading) {
        onSubmit();
      }
    }
  };

  return (
    <div style={{ width: '100%' }}>
      <div className="search-container">
        <textarea
          className="search-textarea"
          placeholder="Enter a statement, news headline, or factual claim to verify..."
          value={claim}
          onChange={(e) => setClaim(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={compact ? 2 : 3}
          disabled={isLoading}
        />
        <div className="search-controls">
          <div className="depth-selector">
            <button
              type="button"
              className={`depth-btn ${depth === 'fast' ? 'active' : ''}`}
              onClick={() => setDepth('fast')}
              disabled={isLoading}
              title="Fast heuristic retrieval & cached verification"
            >
              <Zap size={14} />
              Fast
            </button>
            <button
              type="button"
              className={`depth-btn ${depth === 'deep' ? 'active' : ''}`}
              onClick={() => setDepth('deep')}
              disabled={isLoading}
              title="Deep multi-hop research, proposition decomposition & NLI consensus"
            >
              <Sparkles size={14} />
              Deep Research
            </button>
          </div>

          <button
            type="button"
            className="submit-btn"
            onClick={onSubmit}
            disabled={!claim.trim() || isLoading}
          >
            <span>Verify</span>
            <ArrowUp size={16} />
          </button>
        </div>
      </div>

      {!compact && (
        <div className="example-queries">
          {EXAMPLE_CLAIMS.map((example, idx) => (
            <button
              key={idx}
              className="chip"
              type="button"
              onClick={() => {
                setClaim(example);
              }}
              disabled={isLoading}
            >
              {example}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
