/**
 * Tathvyn API Client with Real-Time Server-Sent Events (SSE) Streaming
 */

const BASE_URL = ''; // Relative URL leverages Vite proxy (/api -> http://localhost:8000)

/**
 * Stream verification progress events in real-time until completion.
 * 
 * @param {string} claim The claim text to verify.
 * @param {string} depth "FAST" or "DEEP"
 * @param {function} onStageUpdate Callback receiving { stage, message, queries?, atomic_claims? }
 * @returns {Promise<object>} Final ClaimVerificationResponse object
 */
export async function streamVerifyClaim(claim, depth = 'FAST', onStageUpdate = () => {}) {
  const normalizedDepth = (depth || 'FAST').toUpperCase();

  try {
    onStageUpdate({
      stage: 'ANALYZING',
      message: 'Connecting to Tathvyn Verification Engine...',
    });

    const response = await fetch(`${BASE_URL}/api/v1/verify/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({ claim, depth: normalizedDepth }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server responded with ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let finalResult = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete trailing fragment in buffer

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data:')) {
          const jsonStr = trimmed.replace(/^data:\s*/, '');
          if (!jsonStr) continue;

          try {
            const eventData = JSON.parse(jsonStr);

            if (eventData.stage === 'COMPLETED') {
              finalResult = eventData.result;
            } else if (eventData.stage === 'FAILED') {
              throw new Error(eventData.error || 'Verification failed');
            } else {
              onStageUpdate(eventData);
            }
          } catch (e) {
            if (e.message !== 'Verification failed') {
              console.warn('Could not parse SSE event:', jsonStr, e);
            } else {
              throw e;
            }
          }
        }
      }
    }

    if (finalResult) {
      return finalResult;
    }

    throw new Error('Stream concluded without returning a completed verdict.');
  } catch (error) {
    console.warn('Streaming error, falling back to standard verification endpoint:', error);
    // Fallback to synchronous endpoint
    return await fallbackSyncVerify(claim, normalizedDepth, onStageUpdate);
  }
}

/**
 * Fallback to standard synchronous check endpoint
 */
async function fallbackSyncVerify(claim, depth, onStageUpdate) {
  onStageUpdate({
    stage: 'SEARCHING',
    message: 'Evaluating multi-source evidence...',
  });

  const res = await fetch(`${BASE_URL}/api/v1/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ claim, depth }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Backend error: ${res.statusText}`);
  }

  return await res.json();
}
