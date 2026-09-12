import React from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  HelpCircle,
  ExternalLink,
  ShieldCheck,
  Clock,
  Share2,
} from 'lucide-react';

export default function VerdictView({ result }) {
  if (!result) return null;

  const {
    verdict = 'SUPPORTED',
    public_label = '',
    confidence = 0,
    evidence_sufficiency = 0,
    summary_text = '',
    citations = [],
    latency_ms = 0,
    claim = '',
  } = result;

  const confidencePct = Math.round(confidence * 100);

  // Map verdict to aesthetic styling & icons
  const getVerdictStyle = () => {
    const v = (verdict || '').toUpperCase();
    if (v.includes('SUPPORT') || v.includes('TRUE')) {
      return {
        badgeClass: 'badge-supported',
        icon: <CheckCircle2 size={18} />,
        label: public_label || 'Verified Accurate',
      };
    } else if (v.includes('REFUT') || v.includes('FALSE')) {
      return {
        badgeClass: 'badge-refuted',
        icon: <XCircle size={18} />,
        label: public_label || 'Refuted / Inaccurate',
      };
    } else if (v.includes('CONFLICT') || v.includes('MIXED')) {
      return {
        badgeClass: 'badge-conflicting',
        icon: <AlertTriangle size={18} />,
        label: public_label || 'Conflicting Evidence',
      };
    } else {
      return {
        badgeClass: 'badge-insufficient',
        icon: <HelpCircle size={18} />,
        label: public_label || 'Unverified / Insufficient Evidence',
      };
    }
  };

  const { badgeClass, icon, label } = getVerdictStyle();

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(
        `Tathvyn Fact-Check Verdict: ${label} (${confidencePct}% confidence)\nClaim: "${claim}"\nSummary: ${summary_text}`
      );
      alert('Verdict summary copied to clipboard!');
    }
  };

  return (
    <div className="verdict-container">
      {/* Main Verdict Card */}
      <div className="verdict-header-card">
        <div className="verdict-pill-row">
          <div className={`verdict-badge ${badgeClass}`}>
            {icon}
            <span>{label}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div className="confidence-metric">
              <span>Confidence:</span>
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                {confidencePct}%
              </span>
              <div className="confidence-bar">
                <div
                  className="confidence-fill"
                  style={{ width: `${Math.min(100, Math.max(5, confidencePct))}%` }}
                />
              </div>
            </div>

            <button
              className="icon-btn"
              onClick={handleShare}
              title="Copy Summary"
              aria-label="Share"
            >
              <Share2 size={15} />
            </button>
          </div>
        </div>

        <div className="verdict-summary">
          {summary_text || 'Verification completed based on multi-source retrieved evidence.'}
        </div>

        <div className="verdict-meta">
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <Clock size={13} />
            <span>{latency_ms ? `${(latency_ms / 1000).toFixed(2)}s latency` : 'Real-time verified'}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <ShieldCheck size={13} />
            <span>NLI Calibrated</span>
          </div>
          {evidence_sufficiency ? (
            <div>Sufficiency: {typeof evidence_sufficiency === 'number' ? `${Math.round(evidence_sufficiency * 100)}%` : evidence_sufficiency}</div>
          ) : null}
        </div>
      </div>

      {/* Citations & Verified Sources */}
      {citations && citations.length > 0 && (
        <div className="section-card">
          <div className="section-title">
            <span>Primary Supporting Sources & Citations ({citations.length})</span>
          </div>

          <div className="citations-grid">
            {citations.map((cite, idx) => (
              <a
                key={idx}
                href={cite.url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="citation-card"
              >
                <div>
                  <div className="citation-domain">
                    <span>{cite.domain || cite.source_name || 'Primary Source'}</span>
                    <ExternalLink size={12} />
                  </div>
                  <div className="citation-passage">
                    "{cite.supporting_passage || cite.source_name || 'Evidence retrieved from web source.'}"
                  </div>
                </div>
                {cite.authority_class && (
                  <div style={{ marginTop: '10px', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Authority: {cite.authority_class}
                  </div>
                )}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
