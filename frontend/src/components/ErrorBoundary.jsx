import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Unhandled Application Exception caught by ErrorBoundary:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleResetState = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
            background: 'var(--bg-color, #0f1012)',
            color: 'var(--text-color, #f2f2f0)',
            fontFamily: "'Inter', -apple-system, sans-serif",
          }}
        >
          <div
            style={{
              maxWidth: '640px',
              width: '100%',
              background: 'var(--surface-elevated, #18191c)',
              border: '1px solid var(--border-faint, #2a2c32)',
              borderRadius: '16px',
              padding: '2.5rem',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
              textAlign: 'center',
            }}
          >
            <div
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'rgba(239, 68, 68, 0.12)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ef4444',
                margin: '0 auto 1.5rem',
              }}
            >
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>

            <h1 style={{ fontSize: '1.6rem', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '0.75rem' }}>
              Application Render Exception
            </h1>

            <p style={{ color: 'var(--text-muted, #9b9ea4)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '2rem' }}>
              Tathvyn caught an unexpected client runtime error. Your application state has been preserved to protect against data corruption.
            </p>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <button
                onClick={this.handleReload}
                style={{
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  background: 'var(--accent-blue, #2563eb)',
                  color: '#ffffff',
                  border: 'none',
                  fontWeight: 600,
                  fontSize: '0.92rem',
                  cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
                }}
              >
                Reload Studio
              </button>

              <button
                onClick={this.handleResetState}
                style={{
                  padding: '0.75rem 1.5rem',
                  borderRadius: '8px',
                  background: 'var(--surface-recessed, #222428)',
                  color: 'var(--text-color, #f2f2f0)',
                  border: '1px solid var(--border-faint, #2a2c32)',
                  fontWeight: 600,
                  fontSize: '0.92rem',
                  cursor: 'pointer',
                }}
              >
                Clear Cache & Restart
              </button>
            </div>

            {this.state.error && (
              <details style={{ marginTop: '2rem', textAlign: 'left', borderTop: '1px solid var(--border-faint, #2a2c32)', paddingTop: '1rem' }}>
                <summary style={{ cursor: 'pointer', fontSize: '0.8rem', color: 'var(--text-muted, #9b9ea4)' }}>
                  Error Trace Information
                </summary>
                <pre
                  style={{
                    marginTop: '0.5rem',
                    padding: '0.75rem',
                    borderRadius: '6px',
                    background: 'rgba(0, 0, 0, 0.4)',
                    color: '#f87171',
                    fontSize: '0.75rem',
                    overflowX: 'auto',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {this.state.error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
