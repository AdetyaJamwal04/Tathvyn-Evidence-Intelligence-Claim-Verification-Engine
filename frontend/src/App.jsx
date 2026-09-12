import React, { useState } from 'react';
import Navbar from './components/Navbar';
import SearchSection from './components/SearchSection';
import StreamingProgress from './components/StreamingProgress';
import ResultsView from './components/ResultsView';
import { streamVerifyClaim } from './api/client';

export default function App() {
  const [claim, setClaim] = useState('');
  const [viewState, setViewState] = useState('home'); // 'home' | 'loading' | 'results'
  const [currentStage, setCurrentStage] = useState('ANALYZING');
  const [stageMessage, setStageMessage] = useState('');
  const [stageData, setStageData] = useState(null);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleVerify = async (queryToVerify) => {
    const targetQuery = queryToVerify || claim;
    if (!targetQuery.trim()) return;

    setViewState('loading');
    setCurrentStage('ANALYZING');
    setStageMessage('Connecting to verification engine...');
    setStageData(null);
    setErrorMessage(null);
    setResult(null);

    try {
      const finalResult = await streamVerifyClaim(targetQuery, 'FAST', (event) => {
        if (event.stage) setCurrentStage(event.stage);
        if (event.message) setStageMessage(event.message);
        setStageData(event);
      });

      setResult(finalResult);
      setViewState('results');
    } catch (err) {
      console.error('Verification failed:', err);
      setErrorMessage(err.message || 'Verification could not be completed.');
      setViewState('home');
    }
  };

  const handleReset = () => {
    setViewState('home');
    setClaim('');
    setResult(null);
    setErrorMessage(null);
  };

  const handleEditQuery = () => {
    setViewState('home');
  };

  return (
    <>
      <Navbar onReset={handleReset} />

      <main id="main-container" className={viewState === 'results' ? 'results-active' : ''}>
        {errorMessage && (
          <div
            style={{
              padding: '1rem 1.25rem',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(220, 38, 38, 0.1)',
              border: '1px solid var(--verdict-refuted)',
              color: 'var(--verdict-refuted)',
              marginBottom: '2rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.9rem',
            }}
          >
            <span>{errorMessage}</span>
            <button
              onClick={() => handleVerify(claim)}
              style={{
                background: 'none',
                border: 'none',
                color: 'inherit',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Retry
            </button>
          </div>
        )}

        {viewState === 'home' && (
          <SearchSection
            claim={claim}
            setClaim={setClaim}
            onVerify={handleVerify}
            isLoading={false}
          />
        )}

        {viewState === 'loading' && (
          <StreamingProgress
            currentStage={currentStage}
            message={stageMessage}
            stageData={stageData}
          />
        )}

        {viewState === 'results' && (
          <ResultsView
            result={result}
            onEditQuery={handleEditQuery}
          />
        )}
      </main>
    </>
  );
}
