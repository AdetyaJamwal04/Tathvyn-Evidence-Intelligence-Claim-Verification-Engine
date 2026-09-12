import React from 'react';
import { Check, Loader2, Sparkles } from 'lucide-react';

const PIPELINE_STEPS = [
  { id: 'enqueue', label: 'Dispatched to Asynchronous Job Queue' },
  { id: 'decompose', label: 'Decomposing claim into verifiable propositions' },
  { id: 'retrieval', label: 'Multi-source evidence search & web cross-referencing' },
  { id: 'nli', label: 'Cross-verifying evidence with NLI consensus' },
  { id: 'synthesis', label: 'Calibrating confidence & generating intelligence verdict' },
];

export default function AsyncProgressTracker({ progressState, depth }) {
  const { status, message } = progressState;

  // Determine active step index based on status & simulated progression
  let activeIndex = 0;
  if (status === 'QUEUED') activeIndex = 0;
  else if (status === 'PROCESSING') activeIndex = depth === 'fast' ? 2 : 3;
  else if (status === 'COMPLETED') activeIndex = 5;

  return (
    <div className="async-tracker-card">
      <div className="tracker-header">
        <div className="tracker-title">
          <div className="pulse-spinner" />
          <span>Verification Engine in Progress</span>
        </div>
        <span className="brand-badge">
          {depth === 'deep' ? 'Deep Research' : 'Fast Path'}
        </span>
      </div>

      <div style={{ marginBottom: '16px', fontSize: '0.92rem', color: 'var(--text-muted)' }}>
        {message || 'Analyzing claim...'}
      </div>

      <div className="steps-flow">
        {PIPELINE_STEPS.map((step, idx) => {
          const isDone = activeIndex > idx;
          const isCurrent = activeIndex === idx;

          return (
            <div
              key={step.id}
              className={`step-item ${isCurrent ? 'active' : ''} ${isDone ? 'completed' : ''}`}
            >
              <div className="step-icon">
                {isDone ? (
                  <Check size={13} strokeWidth={3} />
                ) : isCurrent ? (
                  <Loader2 size={13} className="pulse-spinner" />
                ) : (
                  <span>{idx + 1}</span>
                )}
              </div>
              <span>{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
