import React, { useState } from 'react';
import Navbar from './components/Navbar';
import SearchSection from './components/SearchSection';
import StreamingProgress from './components/StreamingProgress';
import ResultsView from './components/ResultsView';
import ErrorFallback from './components/ErrorFallback';
import { streamVerifyClaim } from './api/client';

export default function App() {
  const [claim, setClaim] = useState('');
  const [viewState, setViewState] = useState('home'); // 'home' | 'loading' | 'results' | 'error'
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
      setErrorMessage(err.message || 'Verification pipeline encountered an unrecoverable error.');
      setViewState('error');
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

        {viewState === 'error' && (
          <ErrorFallback
            claim={claim}
            error={errorMessage}
            onRetry={() => handleVerify(claim)}
            onEditQuery={handleEditQuery}
            onReset={handleReset}
          />
        )}
      </main>
    </>
  );
}
