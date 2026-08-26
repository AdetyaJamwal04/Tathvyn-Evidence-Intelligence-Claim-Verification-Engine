/**
 * Tathvyn — Modern Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navigation View Switching
    const navButtons = document.querySelectorAll('.nav-btn[data-view]');
    const viewPanels = document.querySelectorAll('.view-panel');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetView = btn.getAttribute('data-view');
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            viewPanels.forEach(p => {
                if (p.id === targetView) {
                    p.classList.add('active');
                } else {
                    p.classList.remove('active');
                }
            });

            if (targetView === 'history-view') {
                renderHistory();
            }
        });
    });

    // 2. Elements & Controls
    const form = document.getElementById('verify-form');
    const claimInput = document.getElementById('claim-input');
    const charCount = document.getElementById('char-count');
    const btnSubmit = document.getElementById('btn-submit');
    const depthOptions = document.querySelectorAll('.depth-option');
    const suggestionCards = document.querySelectorAll('.suggestion-card');
    const suggestionsBlock = document.getElementById('suggestions-block');

    const loadingState = document.getElementById('loading-state');
    const resultsPanel = document.getElementById('results-panel');

    // Verdict Elements
    const verdictBanner = document.getElementById('verdict-banner');
    const verdictPublicLabel = document.getElementById('verdict-public-label');
    const verdictInternalLabel = document.getElementById('verdict-internal-label');
    const dialConfidenceNum = document.getElementById('dial-confidence-num');
    const valSufficiency = document.getElementById('val-sufficiency');
    const valLatency = document.getElementById('val-latency');
    const verdictSummaryText = document.getElementById('verdict-summary-text');
    const verdictClaimedText = document.getElementById('verdict-claimed-text');

    const atomicClaimsList = document.getElementById('atomic-claims-list');
    const atomicCountBadge = document.getElementById('atomic-count-badge');
    const citationsList = document.getElementById('citations-list');
    const tabEvidenceCount = document.getElementById('tab-evidence-count');

    // Export Elements
    const markdownReportPreview = document.getElementById('markdown-report-preview');
    const curlSnippetPreview = document.getElementById('curl-snippet-preview');
    const btnCopyMarkdown = document.getElementById('btn-copy-markdown-report');
    const btnDownloadJson = document.getElementById('btn-download-report-json');
    const btnCopyCurl = document.getElementById('btn-copy-curl');

    // History Elements
    const auditHistoryContainer = document.getElementById('audit-history-container');
    const btnPurgeHistory = document.getElementById('btn-purge-history');

    let currentData = null;

    // 3. System Status Health Check
    async function checkHealth() {
        try {
            const res = await fetch('/api/v1/health');
            if (res.ok) {
                const data = await res.json();
                document.getElementById('system-status-pill').textContent = `Online (v${data.version})`;
            }
        } catch {
            document.getElementById('system-status-pill').textContent = 'Local Standalone';
        }
    }
    checkHealth();

    // 4. Character Counter & Textarea Auto-expand
    claimInput.addEventListener('input', () => {
        const len = claimInput.value.length;
        charCount.textContent = `${len} / 1000`;
        claimInput.style.height = 'auto';
        claimInput.style.height = `${Math.min(claimInput.scrollHeight, 180)}px`;
    });

    // 5. Research Depth Radio Selector
    depthOptions.forEach(opt => {
        opt.addEventListener('click', () => {
            depthOptions.forEach(o => o.classList.remove('active'));
            opt.classList.add('active');
            const radio = opt.querySelector('input[type="radio"]');
            if (radio) radio.checked = true;
        });
    });

    // 6. Suggestion Card Clicks
    suggestionCards.forEach(card => {
        card.addEventListener('click', () => {
            const text = card.getAttribute('data-claim');
            claimInput.value = text;
            charCount.textContent = `${text.length} / 1000`;
            claimInput.focus();
            claimInput.dispatchEvent(new Event('input'));
        });
    });

    // 7. Keyboard Shortcuts (Ctrl/Cmd + Enter)
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    });

    // 8. Submit Inquiry Form
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = claimInput.value.trim();
        if (!text) return;

        const depth = document.querySelector('input[name="depth"]:checked')?.value || 'FAST';

        // Transition UI to loading state
        resultsPanel.classList.add('hidden');
        loadingState.classList.remove('hidden');
        if (suggestionsBlock) suggestionsBlock.classList.add('hidden');
        btnSubmit.disabled = true;

        try {
            const res = await fetch('/api/v1/check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ claim: text, depth: depth })
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: 'Verification failed' }));
                throw new Error(err.detail || err.title || `Server error (${res.status})`);
            }

            const data = await res.json();
            currentData = data;
            renderResults(data, text, depth);
            saveHistory(data, text);
            showToast('Evidence examined successfully!');
        } catch (err) {
            showToast(`Error: ${err.message}`, 'error');
        } finally {
            loadingState.classList.add('hidden');
            btnSubmit.disabled = false;
        }
    });

    // 9. Render Verification Results
    function renderResults(data, originalClaim, depth) {
        resultsPanel.classList.remove('hidden');

        // State classes
        verdictBanner.className = 'verdict-banner';
        const labelUpper = (data.public_label || 'UNVERIFIED').toUpperCase();

        if (labelUpper.includes('TRUE')) {
            verdictBanner.classList.add('state-true');
        } else if (labelUpper.includes('FALSE')) {
            verdictBanner.classList.add('state-false');
        } else if (labelUpper.includes('PARTIALLY')) {
            verdictBanner.classList.add('state-mixture');
        }

        verdictPublicLabel.textContent = data.public_label || 'UNVERIFIED';
        verdictInternalLabel.textContent = data.verdict || 'UNKNOWN';

        dialConfidenceNum.textContent = `${Math.round((data.confidence || 0) * 100)}%`;
        valSufficiency.textContent = `${Math.round((data.evidence_sufficiency || 0) * 100)}%`;
        valLatency.textContent = data.latency_ms ? `${(data.latency_ms / 1000).toFixed(2)}s` : '< 1s';

        verdictSummaryText.textContent = data.summary_text || 'Epistemic synthesis complete.';
        verdictClaimedText.textContent = originalClaim;

        // Render Atomic Propositions
        renderAtomicClaims(originalClaim, data.verdict);

        // Render Cited Sources
        renderCitations(data.citations || []);

        // Render Export Dossier
        renderExportDossier(data, originalClaim, depth);
    }

    function renderAtomicClaims(claimText, parentVerdict) {
        atomicClaimsList.innerHTML = '';
        const clauses = claimText.split(/;|\s*,\s*(?:and|whereas|while)\s+/i);
        atomicCountBadge.textContent = `${clauses.length} proposition${clauses.length > 1 ? 's' : ''}`;

        clauses.forEach((c) => {
            const trimmed = c.trim();
            if (!trimmed) return;

            const item = document.createElement('div');
            item.className = 'atomic-item';
            
            const isRefuted = parentVerdict === 'REFUTED';
            const tagClass = isRefuted ? 'contradicted' : (parentVerdict === 'SUPPORTED' ? 'verified' : 'uncertain');
            const tagText = isRefuted ? 'Contradicted' : (parentVerdict === 'SUPPORTED' ? 'Verified' : 'Evaluated');

            item.innerHTML = `
                <span>${trimmed.endsWith('.') ? trimmed : trimmed + '.'}</span>
                <span class="atomic-tag ${tagClass}">${tagText}</span>
            `;
            atomicClaimsList.appendChild(item);
        });
    }

    function renderCitations(citations) {
        citationsList.innerHTML = '';
        tabEvidenceCount.textContent = `${citations.length} source${citations.length > 1 ? 's' : ''}`;

        if (citations.length === 0) {
            citationsList.innerHTML = '<p class="empty-text">No external citations retrieved.</p>';
            return;
        }

        citations.forEach(c => {
            const card = document.createElement('div');
            card.className = 'citation-card';
            card.innerHTML = `
                <div class="citation-head">
                    <a href="${c.url}" target="_blank" rel="noopener noreferrer" class="citation-link">
                        [${c.citation_id}] ${c.source_name || c.domain}
                    </a>
                    <span class="citation-domain">${c.domain || 'web'}</span>
                </div>
                <div class="citation-quote">
                    "${c.supporting_passage || 'Verified by stance classifier.'}"
                </div>
            `;
            citationsList.appendChild(card);
        });
    }

    function renderExportDossier(data, originalClaim, depth) {
        const md = `# Tathvyn Investigation Dossier
**Inquiry:** "${originalClaim}"
**Verdict:** **${data.public_label}** (${Math.round((data.confidence || 0) * 100)}% Confidence)
**Sufficiency:** ${Math.round((data.evidence_sufficiency || 0) * 100)}%

## Synthesis
${data.summary_text}

## Cited Sources
${(data.citations || []).map(c => `- **[${c.citation_id}] ${c.source_name}** (${c.domain})\n  ${c.url}\n  > "${c.supporting_passage}"`).join('\n\n')}
`;
        markdownReportPreview.value = md;

        const curl = `curl -X POST "https://Tathvyn-ai.onrender.com/api/v1/check" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify({ claim: originalClaim, depth: depth }, null, 2)}'`;
        curlSnippetPreview.textContent = curl;
    }

    btnCopyMarkdown.addEventListener('click', () => {
        navigator.clipboard.writeText(markdownReportPreview.value);
        showToast('Markdown dossier copied to clipboard!');
    });

    btnCopyCurl.addEventListener('click', () => {
        navigator.clipboard.writeText(curlSnippetPreview.textContent);
        showToast('cURL snippet copied!');
    });

    btnDownloadJson.addEventListener('click', () => {
        if (!currentData) return;
        const blob = new Blob([JSON.stringify(currentData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Tathvyn_dossier_${currentData.request_id || Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('JSON dossier downloaded!');
    });

    // 10. History Storage
    function getHistory() {
        try {
            return JSON.parse(localStorage.getItem('Tathvyn_history') || '[]');
        } catch {
            return [];
        }
    }

    function saveHistory(data, claimText) {
        const hist = getHistory();
        hist.unshift({
            id: data.request_id || Date.now(),
            claim: claimText,
            public_label: data.public_label,
            confidence: data.confidence,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            data: data
        });
        localStorage.setItem('Tathvyn_history', JSON.stringify(hist.slice(0, 20)));
    }

    function renderHistory() {
        const hist = getHistory();
        auditHistoryContainer.innerHTML = '';

        if (hist.length === 0) {
            auditHistoryContainer.innerHTML = '<p class="empty-text">No past claims examined in this session yet.</p>';
            return;
        }

        hist.forEach(h => {
            const item = document.createElement('div');
            item.className = 'history-item';
            
            const isTrue = (h.public_label || '').includes('TRUE');
            const isFalse = (h.public_label || '').includes('FALSE');
            const color = isTrue ? 'var(--color-true)' : (isFalse ? 'var(--color-false)' : 'var(--color-mixture)');

            item.innerHTML = `
                <div class="history-meta">
                    <span class="history-label" style="color: ${color};">${h.public_label} (${Math.round((h.confidence || 0) * 100)}%)</span>
                    <span class="history-timestamp">${h.time}</span>
                </div>
                <div class="history-title">${h.claim}</div>
            `;

            item.addEventListener('click', () => {
                navButtons[0].click();
                claimInput.value = h.claim;
                charCount.textContent = `${h.claim.length} / 1000`;
                currentData = h.data;
                renderResults(h.data, h.claim, 'FAST');
            });

            auditHistoryContainer.appendChild(item);
        });
    }

    btnPurgeHistory.addEventListener('click', () => {
        localStorage.removeItem('Tathvyn_history');
        renderHistory();
        showToast('History cleared');
    });

    // 11. Toast System
    function showToast(msg) {
        const stack = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = msg;
        stack.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
    }
});
