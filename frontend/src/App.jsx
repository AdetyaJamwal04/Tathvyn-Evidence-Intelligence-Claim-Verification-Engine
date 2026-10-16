import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SearchSection from './components/SearchSection';
import StreamingProgress from './components/StreamingProgress';
import ResultsView from './components/ResultsView';
import ErrorFallback from './components/ErrorFallback';
import { streamVerifyClaim } from './api/client';

export default function App() {
  useEffect(() => {
    if (typeof window !== 'undefined' && window.location.search) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);
  const [claim, setClaim] = useState('');
  const [selectedDepth, setSelectedDepth] = useState('FAST');
  const [viewState, setViewState] = useState('home'); // 'home' | 'loading' | 'results' | 'error'
  const [currentStage, setCurrentStage] = useState('ANALYZING');
  const [stageMessage, setStageMessage] = useState('');
  const [stageData, setStageData] = useState(null);
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleVerify = async (queryToVerify, depth = selectedDepth) => {
    const targetQuery = queryToVerify || claim;
    if (!targetQuery.trim()) return;

    setSelectedDepth(depth);
    setViewState('loading');
    setCurrentStage('ANALYZING');
    setStageMessage(`Connecting to verification engine (${depth === 'DEEP' ? 'Deep Research' : 'Fast Path'})...`);
    setStageData(null);
    setErrorMessage(null);
    setResult(null);

    try {
      const finalResult = await streamVerifyClaim(targetQuery, depth, (event) => {
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
            onRetry={() => handleVerify(claim, selectedDepth)}
            onEditQuery={handleEditQuery}
            onReset={handleReset}
          />
        )}
      </main>
    </>
  );
}

