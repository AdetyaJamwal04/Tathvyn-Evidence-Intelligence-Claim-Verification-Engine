import React, { useState } from 'react';

export default function ResultsView({ result, onEditQuery }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const {
    claim,
    verdict,
    public_label,
    confidence,
    evidence_sufficiency,
    summary_text,
    citations,
    framing_concerns,
  } = result;

  const framingList = Array.isArray(framing_concerns)
    ? framing_concerns
    : (framing_concerns === true ? ['Contextual or framing bias detected in claim structure'] : []);

  const getVerdictDetails = () => {
    const v = (verdict || '').toUpperCase();
    if (v === 'REFUTED') return { className: 'refuted', label: public_label || 'Refuted' };
    if (v === 'PARTIALLY_SUPPORTED' || v === 'CONFLICTING')
      return { className: 'context', label: public_label || 'Context Needed' };
    if (v === 'INSUFFICIENT_EVIDENCE' || v === 'UNVERIFIABLE')
      return { className: 'context', label: public_label || 'Unverified' };
    return { className: 'supported', label: public_label || 'Supported' };
  };

  const { className: verdictClass, label: verdictLabel } = getVerdictDetails();
  const confidencePct = Math.round((confidence || 0) * 100);
  const sufficiencyPct = Math.round((evidence_sufficiency || 0) * 100);

  // Confidence bar color
  const getBarColor = (pct) => {
    if (pct >= 70) return 'var(--verdict-supported)';
    if (pct >= 40) return 'var(--verdict-context)';
    return 'var(--verdict-refuted)';
  };

  // Authority class label styling
  const getAuthorityStyle = (cls) => {
    switch ((cls || '').toUpperCase()) {
      case 'PRIMARY':
        return { bg: 'rgba(34,197,94,0.12)', color: 'var(--verdict-supported)', label: 'Primary Source' };
      case 'SECONDARY':
        return { bg: 'rgba(99,102,241,0.10)', color: '#818cf8', label: 'Secondary Source' };
      case 'CONSULTED':
        return { bg: 'rgba(156,163,175,0.10)', color: 'var(--text-muted)', label: 'Consulted · No Evidence' };
      default:
        return { bg: 'rgba(156,163,175,0.10)', color: 'var(--text-muted)', label: cls };
    }
  };

  const handleCopy = () => {
    const text = `Tathvyn Verdict: ${verdictLabel} (${confidencePct}% confidence)\nClaim: "${claim}"\n\nSummary:\n${summary_text}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportMarkdown = () => {
    const lines = [
      `# Tathvyn Intelligence Verification Report`,
      ``,
      `**Claim:** "${claim}"`,
      `**Verdict:** ${verdictLabel}`,
      `**Epistemic Confidence:** ${confidencePct}%`,
      `**Evidence Sufficiency:** ${sufficiencyPct}%`,
      `**Generated:** ${new Date().toUTCString()}`,
      ``,
      `---`,
      ``,
      `## Epistemic Synthesis`,
      summary_text,
    ];
    if (framingList.length > 0) {
      lines.push(``, `## Framing Concerns`);
      framingList.forEach(fc => lines.push(`- ${fc}`));
    }
    lines.push(``, `---`, ``, `## Sources & Evidence Citations`);
    if (citations && citations.length > 0) {
      citations.forEach((c, idx) => {
        lines.push(`### [${idx + 1}] ${c.source_name || c.domain}`);
        lines.push(`- **URL:** ${c.url}`);
        lines.push(`- **Domain:** ${c.domain}`);
        lines.push(`- **Classification:** ${c.authority_class || 'SECONDARY'}`);
        lines.push(`- **Evidence Excerpt:** "${c.supporting_passage || 'No excerpt available.'}"`);
        lines.push(``);
      });
    } else {
      lines.push(`No corroborating sources found.`);
    }
    const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.setAttribute('download', `Tathvyn-Report-${Date.now()}.md`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => window.print();

  const isConsultedOnly =
    citations && citations.length > 0 && citations.every((c) => c.authority_class === 'CONSULTED');

  const clipSnippet = (text, max = 140) => {
    if (!text) return '';
    const clean = text.replace(/\s+/g, ' ').trim();
    return clean.length > max ? clean.slice(0, max).trimEnd() + '...' : clean;
  };

  return (
    <section id="results-view" className="view-section">
      {/* Query anchor */}
      <div className="query-anchor">
        <p id="active-query" className="active-query-text">"{claim}"</p>
        <button
          id="edit-query-btn"
          className="edit-query-btn"
          onClick={onEditQuery}
          aria-label="Edit Query"
          title="Edit claim"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
          </svg>
        </button>
      </div>

      {/* Verdict */}
      <div className="verdict-container">
        <span className="verdict-badge">VERDICT</span>
        <h2 id="verdict-title" className={`verdict-title ${verdictClass}`}>
          {verdictLabel}
        </h2>

        {/* Confidence + Sufficiency bars */}
        <div className="metrics-row">
          <div className="metric-block">
            <div className="metric-label">
              <span>Epistemic Confidence</span>
              <span className="metric-value" style={{ color: getBarColor(confidencePct) }}>
                {confidencePct}%
              </span>
            </div>
            <div className="metric-bar-track">
              <div
                className="metric-bar-fill"
                style={{ width: `${confidencePct}%`, background: getBarColor(confidencePct) }}
              />
            </div>
          </div>
          <div className="metric-block">
            <div className="metric-label">
              <span>Evidence Sufficiency</span>
              <span className="metric-value" style={{ color: getBarColor(sufficiencyPct) }}>
                {sufficiencyPct}%
              </span>
            </div>
            <div className="metric-bar-track">
              <div
                className="metric-bar-fill"
                style={{ width: `${sufficiencyPct}%`, background: getBarColor(sufficiencyPct) }}
              />
            </div>
          </div>
        </div>

        {/* Framing concerns */}
        {framingList.length > 0 && (
          <div className="framing-concerns">
            {framingList.map((concern, i) => (
              <span key={i} className="framing-chip">⚠ {concern}</span>
            ))}
          </div>
        )}
      </div>

      {/* Synthesis */}
      <div className="synthesis-container">
        <p id="synthesis-text" className="synthesis-text">{summary_text}</p>
        <div className="synthesis-actions">
          <button className="action-btn" id="copy-btn" onClick={handleCopy}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
            <span>{copied ? 'Copied!' : 'Copy Summary'}</span>
          </button>
          <button className="action-btn" onClick={handleExportMarkdown}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            <span>Export Report (.MD)</span>
          </button>
          <button className="action-btn" onClick={handlePrint}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="6 9 6 2 18 2 18 9" />
              <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
              <rect x="6" y="14" width="12" height="8" />
            </svg>
            <span>Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Sources */}
      <div className="sources-container">
        <h3 className="sources-heading">
          {isConsultedOnly ? 'Investigated Sources (No Corroboration Found)' : 'Sources & Citations'}
        </h3>
        {isConsultedOnly && (
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            The following sources were inspected during multi-source web retrieval. None directly corroborated the claim.
          </p>
        )}

        {citations && citations.length > 0 ? (
          <div className="sources-grid" id="sources-grid">
            {citations.map((cite, idx) => {
              const auth = getAuthorityStyle(cite.authority_class);
              return (
                <a
                  key={idx}
                  href={cite.url || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-card"
                  style={{ borderLeft: `3px solid ${auth.color}` }}
                >
                  <div>
                    <div className="source-meta">
                      <span className="source-domain">{cite.domain || 'Primary Source'}</span>
                      <svg className="source-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="7" y1="17" x2="17" y2="7" />
                        <polyline points="7 7 17 7 17 17" />
                      </svg>
                    </div>
                    <div
                      className="source-authority-badge"
                      style={{ background: auth.bg, color: auth.color }}
                    >
                      {auth.label}
                    </div>
                    <div className="source-snippet">
                      "{clipSnippet(cite.supporting_passage || cite.source_name)}"
                    </div>
                  </div>
                </a>
              );
            })}
          </div>
        ) : (
          <div className="sources-empty">
            No corroborating evidence or reporting was found across indexed global news archives,
            government registries, or defense databases for this claim.
          </div>
        )}
      </div>
    </section>
  );
}
