import React, { useState, useEffect } from 'react';
import { checkHealth } from '../api/client';

export default function ErrorFallback({
  claim,
  error,
  onRetry,
  onEditQuery,
  onReset,
}) {
  const [healthStatus, setHealthStatus] = useState(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  useEffect(() => {
    runHealthCheck();
  }, []);

  const runHealthCheck = async () => {
    setIsCheckingHealth(true);
    try {
      const data = await checkHealth();
      setHealthStatus(data);
    } catch {
      setHealthStatus({ status: 'offline', error: 'Could not reach server' });
    } finally {
      setIsCheckingHealth(false);
    }
  };

  const getErrorExplanation = () => {
    const msg = (error || '').toLowerCase();
    if (msg.includes('network') || msg.includes('failed to fetch')) {
      return {
        category: 'Network Disconnection',
        description:
          'Unable to establish a secure connection to the Tathvyn verification gateway. This could be due to network connectivity or firewall rules.',
        suggestion: 'Check your internet connection or verify that the backend service is online.',
      };
    }
    if (msg.includes('502') || msg.includes('503') || msg.includes('504')) {
      return {
        category: 'Gateway / Service Unavailable',
        description:
          'The verification engine or upstream search providers temporarily timed out or were unreachable.',
        suggestion: 'The service may be cycling container instances. Please retry in a few moments.',
      };
    }
    if (msg.includes('429') || msg.includes('rate')) {
      return {
        category: 'Request Rate Limit Exceeded',
        description:
          'Verification quota exceeded or rate-limited by upstream epistemic providers.',
        suggestion: 'Please wait a moment before initiating another comprehensive claim verification.',
      };
    }
    return {
      category: 'Epistemic Pipeline Interruption',
      description:
        error ||
        'The verification pipeline encountered an unrecoverable state while cross-referencing sources.',
      suggestion: 'Try refining the phrasing of the claim to be more specific or try again.',
    };
  };

  const explanation = getErrorExplanation();

  return (
    <div className="fallback-container animate-fade-in" style={{ width: '100%', maxWidth: '720px', margin: '0 auto', padding: '2rem 1rem' }}>
      <div
        className="fallback-card"
        style={{
          background: 'var(--surface-elevated)',
          border: '1px solid var(--border-faint)',
          borderRadius: 'var(--radius-md)',
          padding: '2.5rem',
          boxShadow: '0 12px 32px rgba(0, 0, 0, 0.08)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Ambient Top Glow Line */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '3px',
            background: 'linear-gradient(90deg, #f59e0b, #ef4444, #f59e0b)',
          }}
        />

        {/* Header Icon + Title */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.25rem', marginBottom: '1.5rem' }}>
          <div
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ef4444',
              flexShrink: 0,
            }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                {explanation.category}
              </h2>
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  padding: '0.2rem 0.6rem',
                  borderRadius: '9999px',
                  background: 'rgba(239, 68, 68, 0.12)',
                  color: '#ef4444',
                }}
              >
                Degradation Protection
              </span>
            </div>
            <p style={{ marginTop: '0.35rem', fontSize: '0.92rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              {explanation.description}
            </p>
          </div>
        </div>

        {/* Claim Recap Box */}
        {claim && (
          <div
            style={{
              marginBottom: '1.5rem',
              padding: '0.9rem 1.1rem',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--surface-recessed)',
              border: '1px solid var(--border-faint)',
            }}
          >
            <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>
              Query Under Investigation
            </div>
            <div style={{ fontSize: '0.95rem', fontWeight: 500, color: 'var(--text-primary)', fontStyle: 'italic' }}>
              "{claim}"
            </div>
          </div>
        )}

        {/* Diagnostic System Health Indicator */}
        <div
          style={{
            marginBottom: '1.75rem',
            padding: '1rem',
            borderRadius: 'var(--radius-sm)',
            border: '1px dashed var(--border-faint)',
            background: 'rgba(0, 0, 0, 0.02)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                background:
                  healthStatus?.status === 'healthy'
                    ? '#10b981'
                    : healthStatus?.status === 'offline'
                    ? '#ef4444'
                    : '#f59e0b',
                display: 'inline-block',
                boxShadow:
                  healthStatus?.status === 'healthy'
                    ? '0 0 8px #10b981'
                    : '0 0 8px #f59e0b',
              }}
            />
            <span style={{ fontSize: '0.85rem', fontWeight: 500, color: 'var(--text-primary)' }}>
              Backend Gateway Status:
            </span>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: healthStatus?.status === 'healthy' ? '#10b981' : 'var(--text-muted)' }}>
              {isCheckingHealth
                ? 'Testing connection...'
                : healthStatus?.status === 'healthy'
                ? 'Online & Operational'
                : healthStatus?.status === 'offline'
                ? 'Gateway Offline'
                : 'Degraded State'}
            </span>
          </div>

          <button
            onClick={runHealthCheck}
            disabled={isCheckingHealth}
            style={{
              background: 'none',
              border: '1px solid var(--border-faint)',
              borderRadius: '6px',
              padding: '0.35rem 0.75rem',
              fontSize: '0.78rem',
              fontWeight: 500,
              color: 'var(--text-muted)',
              cursor: isCheckingHealth ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 4v6h-6"></path>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Re-probe
          </button>
        </div>

        {/* Suggestion Note */}
        <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '1.75rem', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
          <span style={{ color: 'var(--accent-blue)', fontWeight: 700 }}>💡 Tip:</span>
          <span>{explanation.suggestion}</span>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            onClick={onRetry}
            style={{
              padding: '0.75rem 1.4rem',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--accent-blue)',
              color: '#ffffff',
              border: 'none',
              fontWeight: 600,
              fontSize: '0.92rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease',
              boxShadow: '0 2px 8px rgba(37, 99, 235, 0.25)',
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 4v6h-6"></path>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Retry Verification
          </button>

          <button
            onClick={onEditQuery}
            style={{
              padding: '0.75rem 1.25rem',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--surface-recessed)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-faint)',
              fontWeight: 600,
              fontSize: '0.92rem',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            Edit Claim Query
          </button>

          <button
            onClick={onReset}
            style={{
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-sm)',
              background: 'transparent',
              color: 'var(--text-muted)',
              border: 'none',
              fontWeight: 500,
              fontSize: '0.88rem',
              cursor: 'pointer',
              marginLeft: 'auto',
            }}
          >
            Return Home
          </button>
        </div>

        {/* Technical Details Toggle */}
        <div style={{ marginTop: '2rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-faint)' }}>
          <button
            onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '0.78rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: 0,
            }}
          >
            <span>{showTechnicalDetails ? '▼ Hide' : '▶ Show'} Technical Diagnostic Report</span>
          </button>

          {showTechnicalDetails && (
            <div
              style={{
                marginTop: '0.75rem',
                padding: '0.85rem',
                borderRadius: '6px',
                background: 'rgba(0, 0, 0, 0.3)',
                color: '#e2e8f0',
                fontFamily: 'monospace',
                fontSize: '0.78rem',
                overflowX: 'auto',
                whiteSpace: 'pre-wrap',
                lineHeight: 1.5,
              }}
            >
              {JSON.stringify(
                {
                  error_message: error,
                  health_probe: healthStatus,
                  timestamp: new Date().toISOString(),
                  connection_online: navigator.onLine,
                },
                null,
                2
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
