import React from 'react';

const STAGES = [
  { key: 'ANALYZING',    label: 'Decomposing claim into verifiable propositions' },
  { key: 'SEARCHING',   label: 'Querying multi-source evidence across web providers' },
  { key: 'RETRIEVING',  label: 'Extracting and segmenting authoritative passages' },
  { key: 'INFERENCE',   label: 'Cross-verifying evidence with NLI consensus models' },
  { key: 'SYNTHESIZING',label: 'Calibrating confidence & synthesizing epistemic verdict' },
];

const getStageIndex = (stage) => {
  const map = {
    ANALYZING: 0, DECOMPOSED: 1, SEARCHING: 1,
    RETRIEVING: 2, INFERENCE: 3, SYNTHESIZING: 4, COMPLETED: 5,
  };
  return map[stage] ?? 0;
};

export default function StreamingProgress({ currentStage, message, stageData }) {
  const currentIndex = getStageIndex(currentStage);

  return (
    <div className="streaming-view view-section">
      <div className="streaming-header">
        <div className="streaming-spinner" />
        <div>
          <div className="streaming-status-title">Verifying Claim Evidence</div>
          <div className="streaming-status-desc">
            {message || 'Synthesizing multi-source intelligence...'}
          </div>
        </div>
      </div>

      <div className="stages-list">
        {STAGES.map((s, idx) => {
          const isDone = currentIndex > idx;
          const isCurrent = currentIndex === idx;
          return (
            <div
              key={s.key}
              className={`stage-row${isCurrent ? ' active' : ''}${isDone ? ' completed' : ''}`}
            >
              <div className="stage-dot">
                {isDone
                  ? <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="1,6 4.5,9.5 11,2" /></svg>
                  : isCurrent
                    ? <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--verdict-supported)' }} />
                    : <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{idx + 1}</span>
                }
              </div>
              <span>{s.label}</span>
            </div>
          );
        })}
      </div>

      {stageData?.queries && stageData.queries.length > 0 && (
        <div
          style={{
            marginTop: '1.25rem',
            paddingTop: '1rem',
            borderTop: '1px solid var(--border-faint)',
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
          }}
        >
          <span style={{ fontWeight: 500, marginRight: '0.5rem' }}>Active Queries:</span>
          {stageData.queries.map((q, i) => (
            <span key={i} style={{ fontStyle: 'italic', marginRight: '0.75rem' }}>
              "{q}"
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
