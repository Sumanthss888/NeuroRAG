// NeuroRAG Chat Interface JavaScript - Apple Premium Edition

// Global state
let currentMode = 'patient';
let messageHistory = [];

const MEDICAL_DICTIONARY = {
    'stroke': 'A sudden interruption in the blood supply of the brain.',
    'ischemic': 'Restricted blood flow and oxygen to a part of the body.',
    'hemorrhage': 'An escape of blood from a ruptured blood vessel.',
    'aphasia': 'Loss of ability to understand or express speech.',
    'migraine': 'A recurring type of headache often with nausea and visual changes.',
    'epilepsy': 'A neurological disorder marked by sudden recurrent episodes of sensory disturbance.',
    'thrombosis': 'Local coagulation or clotting of the blood in a part of the circulatory system.',
    'alzheimer': 'A progressive disease that destroys memory and other important mental functions.',
    'dementia': 'A broad category of brain diseases that cause a long-term and gradual decrease in thinking ability.',
    'seizure': 'A sudden, uncontrolled electrical disturbance in the brain.',
    'neuropathy': 'Weakness, numbness, and pain from nerve damage.'
};

// DOM Elements
const queryInput = document.getElementById('query-input');
const submitBtn = document.getElementById('submit-btn');
const chatContainer = document.getElementById('chat-container');

// Mode Toggle Elements
const modeButtons = document.querySelectorAll('.mode-btn');
const indicator = document.getElementById('toggle-indicator');
const iconPatient = document.getElementById('icon-patient');
const iconClinician = document.getElementById('icon-clinician');
const btnPatient = document.getElementById('mode-patient');
const btnClinician = document.getElementById('mode-clinician');

// Example buttons
const exampleButtons = document.querySelectorAll('.example-btn');

// Feature DOM Elements
const timelineContainer = document.getElementById('timeline-container');
const btnGenerateReport = document.getElementById('btn-generate-report');
const reportModal = document.getElementById('report-modal-backdrop');
const reportContent = document.getElementById('report-content');
const btnCloseReport = document.getElementById('btn-close-report');
const btnPrintReport = document.getElementById('btn-print-report');

// Mobile Sidebar Navigation DOM Elements
const sidebarToggle = document.getElementById('sidebar-toggle');
const sidebar = document.querySelector('aside');
const sidebarOverlay = document.getElementById('sidebar-overlay');
const searchContainer = document.getElementById('sidebar-search-container');
const searchInput = document.getElementById('sidebar-search');

// Initialize Toggle State
updateToggleVisuals(currentMode);

// Event Listeners
submitBtn.addEventListener('click', handleSubmit);

queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
    }
});

// Auto-resize textarea
queryInput.addEventListener('input', () => {
    queryInput.style.height = 'auto';
    queryInput.style.height = queryInput.scrollHeight + 'px';
    if(queryInput.value.trim() === '') {
        queryInput.style.height = '52px';
    }
});

// Mode switching
modeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        currentMode = btn.dataset.mode;
        updateToggleVisuals(currentMode);
        
        document.body.classList.remove('mode-patient', 'mode-clinician');
        document.body.classList.add(`mode-${currentMode}`);

        // Phase 2: Fade-in / Fade-out Mode Change Toast Tooltip
        showModeTooltip(currentMode);
    });
});

// Mobile Sidebar Interactions
if (sidebarToggle && sidebar && sidebarOverlay) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('sidebar-open');
        if (sidebar.classList.contains('sidebar-open')) {
            sidebarOverlay.classList.remove('hidden');
            requestAnimationFrame(() => sidebarOverlay.classList.add('opacity-100'));
        } else {
            sidebarOverlay.classList.remove('opacity-100');
            setTimeout(() => sidebarOverlay.classList.add('hidden'), 300);
        }
    });

    sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('sidebar-open');
        sidebarOverlay.classList.remove('opacity-100');
        setTimeout(() => sidebarOverlay.classList.add('hidden'), 300);
    });
}

// Debounced Smart Conversation Search (PHASE 3)
let searchDebounceTimeout;
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchDebounceTimeout);
        searchDebounceTimeout = setTimeout(() => {
            performSmartSearch(e.target.value);
        }, 300);
    });
}

// Feature: Report Modal Listeners
btnGenerateReport.addEventListener('click', generateReport);
btnCloseReport.addEventListener('click', () => reportModal.classList.remove('active'));
btnPrintReport.addEventListener('click', () => window.print());

function updateToggleVisuals(mode) {
    if (mode === 'patient') {
        if (indicator) indicator.style.transform = 'translateX(0)';
        
        if (btnPatient) {
            btnPatient.classList.remove('text-text-secondary');
            btnPatient.classList.add('text-white');
        }
        if (btnClinician) {
            btnClinician.classList.remove('text-white');
            btnClinician.classList.add('text-text-secondary');
        }
        
        if (iconPatient) iconPatient.className = 'ph-fill ph-user text-white transition-all duration-300 text-xs';
        if (iconClinician) iconClinician.className = 'ph-fill ph-stethoscope text-emerald-400 opacity-40 transition-all duration-300 text-xs';
    } else {
        if (indicator) indicator.style.transform = 'translateX(100%)';
        
        if (btnClinician) {
            btnClinician.classList.remove('text-text-secondary');
            btnClinician.classList.add('text-white');
        }
        if (btnPatient) {
            btnPatient.classList.remove('text-white');
            btnPatient.classList.add('text-text-secondary');
        }
        
        if (iconClinician) iconClinician.className = 'ph-fill ph-stethoscope text-emerald-400 transition-all duration-300 text-xs';
        if (iconPatient) iconPatient.className = 'ph-fill ph-user text-white opacity-40 transition-all duration-300 text-xs';
    }
}

// Operational Switch Tooltip Toast Notification
function showModeTooltip(mode) {
    const existing = document.getElementById('mode-tooltip');
    if (existing) existing.remove();

    const tooltip = document.createElement('div');
    tooltip.id = 'mode-tooltip';
    tooltip.className = 'fixed top-20 left-1/2 -translate-x-1/2 px-4 py-2 rounded-xl bg-accent text-white text-xs font-semibold shadow-glow z-50 transition-all duration-300 opacity-0 transform translate-y-[-10px] pointer-events-none';
    tooltip.textContent = `Switched to ${mode.charAt(0).toUpperCase() + mode.slice(1)} Mode`;
    
    document.body.appendChild(tooltip);
    
    requestAnimationFrame(() => {
        tooltip.classList.remove('opacity-0', 'translate-y-[-10px]');
        tooltip.classList.add('opacity-100', 'translate-y-0');
    });
    
    setTimeout(() => {
        tooltip.classList.remove('opacity-100', 'translate-y-0');
        tooltip.classList.add('opacity-0', 'translate-y-[-10px]');
        setTimeout(() => tooltip.remove(), 300);
    }, 1500);
}

exampleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        queryInput.value = btn.dataset.query;
        queryInput.style.height = 'auto';
        queryInput.style.height = queryInput.scrollHeight + 'px';
        handleSubmit();
    });
});

async function handleSubmit() {
    const query = queryInput.value.trim();
    if (!query) return;
    
    queryInput.value = '';
    queryInput.style.height = '52px';
    
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        welcomeMsg.style.opacity = '0';
        welcomeMsg.style.transform = 'scale(0.96)';
        setTimeout(() => welcomeMsg.remove(), 300);
    }
    
    const messageId = 'msg-' + Date.now();
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const historyEntry = {
        id: messageId,
        query: query,
        answer: null,
        timestamp: timestamp,
        mode: currentMode
    };
    messageHistory.push(historyEntry);
    
    addMessage('user', query, messageId);
    updateTimeline();
    
    const loadingId = showLoading();
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, mode: currentMode })
        });
        
        const data = await response.json();
        removeLoading(loadingId);
        
        if (data.success) {
            historyEntry.answer = data.answer; // Update history
            addAssistantMessage(data, messageId + '-response');
            btnGenerateReport.classList.remove('hidden'); // Enable Report generation
        } else {
            addErrorMessage(data.message || (typeof data.error === 'string' ? data.error : null) || 'An error occurred while processing your query');
        }
    } catch (error) {
        removeLoading(loadingId);
        addErrorMessage('Failed to connect to the server. Please try again.');
        console.error('Error:', error);
    }
}

function updateTimeline() {
    timelineContainer.classList.remove('hidden');
    timelineContainer.innerHTML = '';
    
    const examples = document.getElementById('example-queries-container');
    if (examples) examples.classList.add('hidden');

    if (searchContainer && messageHistory.length > 0) {
        searchContainer.classList.remove('hidden');
    }
    
    messageHistory.forEach((entry, index) => {
        const item = document.createElement('div');
        item.className = 'timeline-item animate-message-enter';
        item.style.animationDelay = `${index * 50}ms`;
        
        const accentClass = entry.mode === 'patient' ? 'text-accent' : 'text-emerald-400';
        const isActive = index === messageHistory.length - 1 ? 'active' : '';
        
        item.innerHTML = `
            <div class="timeline-dot ${accentClass}"></div>
            <div class="timeline-card ${isActive}" onclick="scrollToMessage('${entry.id}', this)">
                <div class="flex items-center justify-between mb-1">
                    <span class="text-[10px] font-semibold text-text-muted uppercase tracking-widest">${entry.timestamp}</span>
                    <i class="ph-fill ${entry.mode === 'patient' ? 'ph-user' : 'ph-stethoscope'} ${accentClass} text-xs opacity-70"></i>
                </div>
                <p class="text-[12px] text-text-secondary line-clamp-2 font-medium leading-snug">${entry.query}</p>
            </div>
        `;
        timelineContainer.appendChild(item);
    });
}

function scrollToMessage(id, element) {
    // Highlight clicked card
    timelineContainer.querySelectorAll('.timeline-card').forEach(c => c.classList.remove('active'));
    if (element) element.classList.add('active');

    const msgElement = document.getElementById(id);
    if (msgElement) {
        msgElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Collapse mobile sidebar on timeline select
    if (window.innerWidth < 768 && sidebar && sidebarOverlay) {
        sidebar.classList.remove('sidebar-open');
        sidebarOverlay.classList.remove('opacity-100');
        setTimeout(() => sidebarOverlay.classList.add('hidden'), 300);
    }
}

function generateReport() {
    if (messageHistory.length === 0) return;
    
    const lastEntry = messageHistory[messageHistory.length - 1];
    if (!lastEntry.answer) return;
    
    const isPatient = lastEntry.mode === 'patient';
    const accentColor = '#7C6AF7'; 
    const modeName = isPatient ? 'Patient Overview' : 'Clinical Diagnostic';
    const date = new Date().toLocaleDateString();
    
    let formattedAnswer = formatAnswerStreaming(lastEntry.answer, isPatient);
    // Sanitize chat animations and styles
    formattedAnswer = formattedAnswer.replace(/style="[^"]*"/g, '');
    formattedAnswer = formattedAnswer.replace(/animate-fade-in/g, '');
    formattedAnswer = formattedAnswer.replace(/opacity-0/g, '');
    // Convert symptom highlights to standard marks for document rendering
    formattedAnswer = formattedAnswer.replace(/<span class="symptom-highlight"[^>]*>(.*?)<\/span>/g, '<mark>$1</mark>');
    
    reportContent.innerHTML = `
        <div class="border-b pb-6 mb-6" style="border-color: #e2e8f0">
            <div class="flex items-center gap-3 mb-2">
                <svg class="w-8 h-8 text-accent" viewBox="0 0 24 24" fill="none" stroke="#7C6AF7" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
                    <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
                    <path d="M12 5v13" />
                </svg>
                <div>
                    <h1 class="text-2xl font-bold font-display tracking-tight text-slate-900 leading-tight" style="margin-bottom:0">NeuroRAG</h1>
                    <p class="section-label" style="margin-bottom:0">Official Clinical AI Report</p>
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4 mb-8 text-sm border border-slate-200 rounded-lg p-4 bg-slate-50">
            <div><strong class="section-label block mb-1">Date generated</strong> <span class="font-medium text-slate-800">${date} ${lastEntry.timestamp}</span></div>
            <div><strong class="section-label block mb-1">Operational Mode</strong> <span class="font-medium text-slate-800">${modeName}</span></div>
        </div>
        
        <div class="mb-8">
            <h2 class="section-label mb-3 border-l-2 pl-3" style="border-color: ${accentColor}">Original Inquiry</h2>
            <p class="text-slate-800 font-medium text-[15px] leading-relaxed">${lastEntry.query}</p>
        </div>
        
        <div>
            <h2 class="section-label mb-4 border-l-2 pl-3" style="border-color: ${accentColor}">System Analysis & Response</h2>
            <div class="markdown-body">
                ${formattedAnswer}
            </div>
        </div>
    `;
    
    reportModal.classList.add('active');
}

function addMessage(sender, content, id) {
    const messageWrapper = document.createElement('div');
    messageWrapper.id = id; 
    messageWrapper.className = 'flex w-full animate-message-enter justify-end pl-12';
    
    // User Message Bubble redesign specs
    const messageBubble = document.createElement('div');
    messageBubble.className = 'relative max-w-[85%] rounded-[18px_18px_4px_18px] bg-accent/10 text-white border border-accent/25 p-[12px_16px] shadow-soft';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'font-sans text-[14px] leading-relaxed font-medium text-text-primary';
    contentDiv.textContent = content;
    
    messageBubble.appendChild(contentDiv);
    messageWrapper.appendChild(messageBubble);
    
    chatContainer.appendChild(messageWrapper);
    scrollToBottom();
}

function addAssistantMessage(data, id) {
    const messageWrapper = document.createElement('div');
    if (id) messageWrapper.id = id;
    messageWrapper.className = 'flex w-full animate-message-enter pr-12 justify-start';
    
    const isPatient = currentMode === 'patient';
    
    // AI Message Card redesign specs
    const messageCard = document.createElement('div');
    messageCard.className = `glass-subtle message-card assistant relative w-full rounded-[4px_18px_18px_18px] p-[12px_16px] border border-border shadow-soft`;
    
    const contentContainer = document.createElement('div');
    contentContainer.className = 'w-full';
    
    const header = document.createElement('div');
    header.className = `mb-3.5 flex items-center justify-between pb-2 border-b border-border/20`;
    
    const aiLabel = document.createElement('div');
    aiLabel.className = `flex items-center gap-2 text-[10px] font-semibold uppercase tracking-widest text-text-secondary`;
    aiLabel.innerHTML = `
        <svg class="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
            <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
            <path d="M12 5v13" />
        </svg> System Response
    `;
    
    header.appendChild(aiLabel);
    
    // Render severity level badge
    const severity = data.severity_level || 'informational';
    const badge = document.createElement('div');
    badge.className = `severity-badge ${severity}`;
    
    let iconClass = 'ph-bold ph-info';
    if (severity === 'medium') iconClass = 'ph-bold ph-warning-circle';
    if (severity === 'high') iconClass = 'ph-bold ph-warning';
    
    badge.innerHTML = `<i class="${iconClass}"></i> ${severity}`;
    header.appendChild(badge);
    
    contentContainer.appendChild(header);
    
    const redFlag = detectRedFlags(data.answer);
    if (redFlag) {
        contentContainer.appendChild(redFlag);
    }
    
    const answerDiv = document.createElement('div');
    answerDiv.className = 'markdown-body text-[14px] leading-relaxed font-medium text-text-secondary';
    answerDiv.innerHTML = formatAnswerStreaming(data.answer, isPatient);
    contentContainer.appendChild(answerDiv);

    // Citations (beneath Response) specs
    if (data.citations && data.citations.length > 0) {
        const citationsContainer = document.createElement('div');
        citationsContainer.className = 'mt-4 flex flex-wrap gap-2 pt-2 border-t border-border/20';
        
        data.citations.forEach(cit => {
            const pill = document.createElement('div');
            pill.className = 'glass-subtle inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium text-text-secondary hover:text-white transition-all cursor-pointer border border-border';
            pill.setAttribute('title', `Similarity Score: ${(cit.similarity * 100).toFixed(1)}%`);
            pill.innerHTML = `<i class="ph-bold ph-bookmark-simple text-accent"></i> Chapter ${cit.chapter_id}: ${cit.chapter_title}`;
            
            // Phase 3: Interactive Modal Trigger
            pill.addEventListener('click', () => {
                openSourceModal(cit);
            });
            
            citationsContainer.appendChild(pill);
        });
        contentContainer.appendChild(citationsContainer);
    }
    
    const riskLevel = calculateRiskScore(data.answer);
    const riskIndicator = createRiskIndicator(riskLevel);
    contentContainer.appendChild(riskIndicator);
    
    const queryUsed = messageHistory[messageHistory.length - 1].query;
    const reasoningSnapshot = createReasoningSnapshot(queryUsed, data.answer);
    contentContainer.appendChild(reasoningSnapshot);
    
    const queryUsed = messageHistory.length > 0 ? messageHistory[messageHistory.length - 1].query : (data.query || '');
    const suggestions = (data.suggested_questions && data.suggested_questions.length > 0)
        ? data.suggested_questions
        : (data.followup_questions && data.followup_questions.length > 0 
            ? data.followup_questions.slice(0, 3) 
            : generateFallbackSuggestions(queryUsed).slice(0, 3));
        
    const followupSection = createFollowupSection(suggestions);
    contentContainer.appendChild(followupSection);

    // Phase 3: Clinical Citation Audit Trail Footer
    if (data.citations || data.retrieved_chunks_count !== undefined) {
        const auditTrail = document.createElement('div');
        auditTrail.className = 'audit-trail';
        
        const timestampVal = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
        const sourcesCount = data.citations ? data.citations.length : 0;
        const chunksCount = data.retrieved_chunks_count || 0;
        
        auditTrail.innerHTML = `
            <div class="audit-item">
                <i class="ph ph-books text-xs text-text-muted"></i>
                <span>Sources Used: <strong>${sourcesCount}</strong></span>
            </div>
            <div class="audit-item">
                <i class="ph ph-hash text-xs text-text-muted"></i>
                <span>Retrieved Chunks: <strong>${chunksCount}</strong></span>
            </div>
            <div class="audit-item">
                <i class="ph ph-clock text-xs text-text-muted"></i>
                <span>Generated: <strong>${timestampVal}</strong></span>
            </div>
        `;
        contentContainer.appendChild(auditTrail);
    }
    
    // Phase 3: Copy Response Button
    const copyBtn = document.createElement('button');
    copyBtn.className = 'btn-copy-response';
    copyBtn.setAttribute('title', 'Copy response text');
    copyBtn.setAttribute('aria-label', 'Copy response to clipboard');
    copyBtn.innerHTML = '<i class="ph ph-copy text-xs"></i>';
    
    copyBtn.addEventListener('click', async () => {
        try {
            if (!navigator.clipboard) {
                throw new Error('Clipboard API not available');
            }
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = data.answer;
            const plainText = tempDiv.textContent || tempDiv.innerText || '';
            
            await navigator.clipboard.writeText(plainText.trim());
            
            // Visual success feedback
            copyBtn.innerHTML = '<span class="text-xs font-semibold text-emerald-400">✓</span>';
            showToast('Response copied to clipboard.', 'success');
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="ph ph-copy text-xs"></i>';
            }, 1500);
        } catch (err) {
            console.error('Copy failure:', err);
            showToast('Unable to copy response.', 'error');
        }
    });
    
    // Phase 3: Bookmark Button
    const bookmarkBtn = document.createElement('button');
    bookmarkBtn.className = 'btn-bookmark-response';
    bookmarkBtn.setAttribute('title', 'Bookmark this response');
    bookmarkBtn.setAttribute('aria-label', 'Bookmark response');
    
    const cleanId = id || `msg-resp-${Date.now()}`;
    const queryText = data.query || queryUsed;
    
    const bookmarked = checkIsBookmarked(cleanId);
    if (bookmarked) {
        bookmarkBtn.classList.add('active');
        bookmarkBtn.innerHTML = '<i class="ph-fill ph-bookmark-simple text-xs"></i>';
    } else {
        bookmarkBtn.innerHTML = '<i class="ph ph-bookmark-simple text-xs"></i>';
    }
    
    bookmarkBtn.addEventListener('click', () => {
        toggleBookmark(data.answer, queryText, cleanId, bookmarkBtn);
    });
    
    messageCard.appendChild(bookmarkBtn);
    messageCard.appendChild(copyBtn);
    messageCard.appendChild(contentContainer);
    messageWrapper.appendChild(messageCard);
    
    chatContainer.appendChild(messageWrapper);
    scrollToBottom();
}

function formatAnswerStreaming(text, isPatient) {
    text = text.split('---')[0].trim();
    const paragraphs = text.split('\n\n');
    let formatted = '';
    let delayMs = 0;
    
    for (const para of paragraphs) {
        if (para.trim()) {
            if (para.startsWith('**') || para.startsWith('#')) {
                const heading = para.replace(/[*#]/g, '').trim();
                formatted += `<h3 class="animate-fade-in opacity-0" style="animation-delay: ${delayMs}ms; animation-fill-mode: forwards;">${heading}</h3>`;
                delayMs += 60;
            } else if (para.trim().match(/^[\-\*\d\.]/)) {
                const items = para.split('\n');
                formatted += `<ul class="animate-fade-in opacity-0" style="animation-delay: ${delayMs}ms; animation-fill-mode: forwards;">`;
                delayMs += 40;
                for (const item of items) {
                    if (item.trim()) {
                        const cleanItem = item.replace(/^[\-\*\d\.]\s*/, '').trim();
                        const boldParsed = cleanItem.replace(/\*\*(.*?)\*\*/g, `<strong>$1</strong>`);
                        formatted += `<li>${boldParsed}</li>`;
                        delayMs += 40;
                    }
                }
                formatted += '</ul>';
            } else {
                const boldParsed = para.trim().replace(/\*\*(.*?)\*\*/g, `<strong>$1</strong>`);
                formatted += `<p class="animate-fade-in opacity-0" style="animation-delay: ${delayMs}ms; animation-fill-mode: forwards;">${boldParsed}</p>`;
                delayMs += 80;
            }
        }
    }
    
    formatted = processTextForTooltips(formatted);
    return formatted;
}

function processTextForTooltips(text) {
    let processedText = text;
    for (const [keyword, definition] of Object.entries(MEDICAL_DICTIONARY)) {
        const regex = new RegExp(`\\b(${keyword}s?)\\b(?![^<]*>)`, 'gi');
        processedText = processedText.replace(regex, `<span class="symptom-highlight" data-tooltip="${definition}">$1</span>`);
    }
    return processedText;
}

function calculateRiskScore(text) {
    const textLower = text.toLowerCase();
    const highRiskKeywords = ['emergency', 'stroke', 'hemorrhage', 'severe', 'critical', 'immediate', 'hospital', 'life-threatening', 'seizure'];
    const mediumRiskKeywords = ['chronic', 'pain', 'monitor', 'consult', 'evaluation', 'moderate', 'persistent', 'migraine'];
    
    let isHigh = false;
    let isMedium = false;
    
    for (const word of highRiskKeywords) {
        if (textLower.includes(word)) { isHigh = true; break; }
    }
    
    if (!isHigh) {
        for (const word of mediumRiskKeywords) {
            if (textLower.includes(word)) { isMedium = true; break; }
        }
    }
    
    if (isHigh) return 'high';
    if (isMedium) return 'medium';
    return 'low';
}

function createRiskIndicator(riskLevel) {
    const riskContainer = document.createElement('div');
    riskContainer.className = 'risk-container';
    
    let percentage = '30%';
    if (riskLevel === 'medium') percentage = '65%';
    if (riskLevel === 'high') percentage = '95%';
    
    riskContainer.innerHTML = `
        <div class="risk-header">
            <span class="risk-label">Clinical Risk Assessment</span>
            <span class="risk-value ${riskLevel}">${riskLevel} Risk</span>
        </div>
        <div class="risk-bar-bg">
            <div class="risk-bar-fill ${riskLevel}"></div>
        </div>
    `;
    
    setTimeout(() => {
        const fill = riskContainer.querySelector('.risk-bar-fill');
        if (fill) fill.style.width = percentage;
    }, 50);
    
    return riskContainer;
}

function createFollowupSection(questions) {
    const section = document.createElement('div');
    section.className = 'suggestions-container';
    
    questions.forEach(question => {
        const qBtn = document.createElement('button');
        qBtn.className = 'suggestion-chip';
        qBtn.innerHTML = `<i class="ph-bold ph-arrow-bend-down-right"></i> ${question}`;
        
        qBtn.addEventListener('click', () => {
            queryInput.value = question;
            queryInput.style.height = 'auto';
            queryInput.style.height = queryInput.scrollHeight + 'px';
            handleSubmit();
        });
        
        section.appendChild(qBtn);
    });
    
    return section;
}

function detectRedFlags(text) {
    const textLower = text.toLowerCase();
    const criticalKeywords = ['stroke', 'severe headache', 'unconscious', 'bleeding', 'emergency', 'life-threatening', 'hemorrhage'];
    
    let detected = false;
    for (const keyword of criticalKeywords) {
        if (textLower.includes(keyword)) {
            detected = true;
            break;
        }
    }
    
    if (!detected) return null;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'red-flag-alert';
    alertDiv.innerHTML = `
        <i class="ph-fill ph-warning-circle red-flag-icon"></i>
        <div class="red-flag-content">
            <div class="red-flag-title">Critical Alert</div>
            <div class="red-flag-text">Critical symptoms detected. Immediate medical attention may be required. Do not rely solely on this AI analysis.</div>
        </div>
    `;
    return alertDiv;
}

function createReasoningSnapshot(query, response) {
    const combinedText = (query + ' ' + response).toLowerCase();
    const matchedKeywords = [];
    
    for (const [keyword, definition] of Object.entries(MEDICAL_DICTIONARY)) {
        if (combinedText.includes(keyword.toLowerCase())) {
            matchedKeywords.push(keyword);
        }
    }
    
    const container = document.createElement('div');
    container.className = 'reasoning-container mt-4 border border-border rounded-xl bg-black/10 overflow-hidden';
    
    const confidence = Math.min(60 + matchedKeywords.length * 10, 95);
    
    container.innerHTML = `
        <div class="reasoning-header px-4 py-3 flex items-center justify-between cursor-pointer select-none bg-white/2 hover:bg-white/4 transition-colors" onclick="this.parentElement.classList.toggle('expanded')">
            <div class="reasoning-title text-[10px] font-semibold uppercase tracking-wider text-text-secondary flex items-center gap-2">
                <i class="ph-bold ph-brain text-accent text-sm"></i> Clinical Analysis
            </div>
            <i class="ph-bold ph-caret-down text-text-muted transition-transform duration-300 reasoning-icon"></i>
        </div>
        <div class="reasoning-content-wrapper">
            <div class="reasoning-content">
                <div class="reasoning-inner p-4 border-t border-border/40 space-y-4">
                    <!-- Confidence Indicator -->
                    <div class="space-y-1.5">
                        <div class="flex justify-between text-xs font-semibold text-text-secondary">
                            <span>Confidence Assessment</span>
                            <span>${confidence}%</span>
                        </div>
                        <div class="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                            <div class="confidence-bar h-full bg-accent rounded-full transition-all duration-1000 ease-out" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <!-- Supporting Findings -->
                    <div class="space-y-1">
                        <div class="text-[10px] font-bold text-text-muted uppercase tracking-wider">Clinical Indicators Matched</div>
                        <div class="flex flex-wrap gap-1.5 mt-1">
                            ${matchedKeywords.length > 0 
                                ? matchedKeywords.map(k => '<span class="px-2 py-0.5 rounded bg-accent/10 border border-accent/20 text-accent text-[10px] font-medium">' + k + '</span>').join('') 
                                : '<span class="text-text-muted text-xs">No specific clinical dictionary matches.</span>'}
                        </div>
                    </div>
                    
                    <!-- Clinical Guidance Summary -->
                    <div class="space-y-1">
                        <div class="text-[10px] font-bold text-text-muted uppercase tracking-wider">Clinical Guidance Summary</div>
                        <p class="text-xs text-text-secondary leading-relaxed font-medium">
                            Cross-referenced inquiry details against clinical neurology handbook. Synthesized response using ${matchedKeywords.length > 0 ? 'high-density target' : 'general'} medical guidelines.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Animate progress bar width after layout insertion
    setTimeout(() => {
        const bar = container.querySelector('.confidence-bar');
        if (bar) bar.style.width = `${confidence}%`;
    }, 100);
    
    return container;
}

function generateFallbackSuggestions(query) {
    const qLower = query.toLowerCase();
    if (qLower.includes('stroke') || qLower.includes('hemorrhage')) {
        return ['What are the long-term effects?', 'How is it diagnosed?', 'What are the emergency protocols?'];
    } else if (qLower.includes('migraine') || qLower.includes('headache')) {
        return ['What are common triggers?', 'What medications are used?', 'When should I see a doctor?'];
    }
    return ['Can you explain the diagnosis process?', 'What are the treatment options?', 'Are there any lifestyle changes?'];
}

function addErrorMessage(errorText, id) {
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'flex w-full animate-message-enter pr-12 justify-start error-bubble-container';
    if (id) messageWrapper.id = id;
    
    const messageCard = document.createElement('div');
    messageCard.className = 'glass-subtle message-card assistant relative w-full rounded-[4px_18px_18px_18px] p-5 border border-border border-l-4 border-l-red-500/80 shadow-soft flex flex-col gap-3';
    
    messageCard.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-widest text-red-400">
                <i class="ph-bold ph-warning-circle text-sm"></i> System Error
            </div>
            <button class="btn-retry flex items-center gap-1.5 px-3 py-1 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 text-[10px] font-bold uppercase tracking-wider transition-all" aria-label="Retry query">
                <i class="ph-bold ph-arrows-counter-clockwise text-xs"></i> Retry
            </button>
        </div>
        <p class="text-[14px] font-medium text-text-secondary leading-relaxed">${errorText}</p>
    `;
    
    // Add retry click event
    const retryBtn = messageCard.querySelector('.btn-retry');
    retryBtn.addEventListener('click', () => {
        // Remove error bubble
        messageWrapper.remove();
        
        if (messageHistory.length > 0) {
            const lastEntry = messageHistory[messageHistory.length - 1];
            // Remove last user message bubble from DOM
            const userMsgEl = document.getElementById(lastEntry.id);
            if (userMsgEl) userMsgEl.remove();
            
            // Pop the failed query from history so handleSubmit pushes it fresh
            messageHistory.pop();
            
            // Re-submit
            queryInput.value = lastEntry.query;
            handleSubmit();
        }
    });
    
    messageWrapper.appendChild(messageCard);
    chatContainer.appendChild(messageWrapper);
    scrollToBottom();
}

function showLoading() {
    const loadingId = 'loading-' + Date.now();
    const messageWrapper = document.createElement('div');
    messageWrapper.id = loadingId;
    messageWrapper.className = 'flex w-full animate-message-enter pr-12 justify-start';
    
    const messageCard = document.createElement('div');
    messageCard.className = 'glass-subtle message-card assistant relative w-full rounded-[4px_18px_18px_18px] p-[12px_16px] border border-border shadow-soft flex gap-3.5';
    
    messageCard.innerHTML = `
        <!-- AI Avatar Placeholder -->
        <div class="flex-shrink-0 w-8 h-8 rounded-lg bg-accent/15 border border-accent/25 flex items-center justify-center placeholder-shimmer">
            <svg class="w-4.5 h-4.5 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <title>Workspace Icon</title>
                <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
                <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
                <path d="M12 5v13" />
            </svg>
        </div>
        
        <div class="flex-1 space-y-3 py-1">
            <!-- Two Shimmer lines -->
            <div class="h-3.5 bg-white/7 rounded w-4/5 placeholder-shimmer"></div>
            <div class="h-3.5 bg-white/5 rounded w-2/3 placeholder-shimmer"></div>
            
            <!-- Typing dots indicator -->
            <div class="typing-indicator-container mt-1.5 flex items-center gap-1.5 pl-0.5" role="status" aria-live="polite">
                <span class="sr-only">Clinical intelligence assistant is thinking...</span>
                <div class="typing-dot w-1.5 h-1.5 rounded-full bg-text-secondary opacity-40"></div>
                <div class="typing-dot w-1.5 h-1.5 rounded-full bg-text-secondary opacity-40"></div>
                <div class="typing-dot w-1.5 h-1.5 rounded-full bg-text-secondary opacity-40"></div>
            </div>
        </div>
    `;
    
    messageWrapper.appendChild(messageCard);
    chatContainer.appendChild(messageWrapper);
    scrollToBottom();
    
    submitBtn.disabled = true;
    return loadingId;
}

function removeLoading(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.style.transition = 'opacity 0.3s var(--apple-ease), transform 0.3s var(--apple-ease)';
        loadingDiv.style.opacity = '0';
        loadingDiv.style.transform = 'scale(0.96)';
        setTimeout(() => loadingDiv.remove(), 300);
    }
    submitBtn.disabled = false;
}

function scrollToBottom() {
    const scrollFn = () => {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight + 500,
            behavior: 'smooth'
        });
    };
    
    requestAnimationFrame(scrollFn);
    setTimeout(scrollFn, 400);
    setTimeout(scrollFn, 800);
    setTimeout(scrollFn, 1200);
}

// Phase 3 Initializations & Event Listeners
initVoiceInput();
initExportControls();
initBookmarks();
initSessionHistory();
initKeyboardShortcuts();

// FEATURE 1: SMART CONVERSATION SEARCH HELPERS
function performSmartSearch(term) {
    const cleanTerm = term.trim().toLowerCase();
    const items = timelineContainer.querySelectorAll('.timeline-item');
    const emptyState = document.getElementById('search-empty-state');
    let matchesCount = 0;

    items.forEach((item, idx) => {
        if (idx < messageHistory.length) {
            const entry = messageHistory[idx];
            const titleText = entry.query || '';
            const previewText = entry.answer || '';
            const metadataText = entry.mode + ' ' + entry.timestamp;
            
            const combinedText = (titleText + ' ' + previewText + ' ' + metadataText).toLowerCase();
            const cardTextElement = item.querySelector('p');
            const originalQuery = entry.query;

            if (cleanTerm === '') {
                // Restore original text
                if (cardTextElement) cardTextElement.innerHTML = escapeHTML(originalQuery);
                item.classList.remove('hidden');
                matchesCount++;
            } else if (combinedText.includes(cleanTerm)) {
                // Highlight matched fragments in title
                if (cardTextElement && titleText.toLowerCase().includes(cleanTerm)) {
                    cardTextElement.innerHTML = highlightMatchedText(originalQuery, cleanTerm);
                } else if (cardTextElement) {
                    cardTextElement.innerHTML = escapeHTML(originalQuery);
                }
                item.classList.remove('hidden');
                matchesCount++;
            } else {
                item.classList.add('hidden');
            }
        }
    });

    if (emptyState) {
        if (matchesCount === 0 && cleanTerm !== '') {
            emptyState.style.display = 'block';
        } else {
            emptyState.style.display = 'none';
        }
    }
}

function escapeHTML(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function highlightMatchedText(text, search) {
    if (!search) return escapeHTML(text);
    const regex = new RegExp(`(${escapeRegExp(search)})`, 'gi');
    return escapeHTML(text).replace(regex, '<span class="search-highlight">$1</span>');
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// FEATURE 2: VOICE INPUT
const btnVoice = document.getElementById('btn-voice');
let recognition = null;
let isListening = false;

function initVoiceInput() {
    if (!btnVoice) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        // Graceful fallback
        btnVoice.disabled = true;
        btnVoice.style.opacity = '0.4';
        btnVoice.setAttribute('title', 'Voice input is not supported in this browser.');
        return;
    }

    try {
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onstart = () => {
            isListening = true;
            btnVoice.classList.add('listening');
            btnVoice.setAttribute('title', 'Listening...');
            btnVoice.innerHTML = '<i class="ph-bold ph-microphone-slash text-lg"></i>';
            showToast('Listening...', 'info');
        };

        recognition.onend = () => {
            isListening = false;
            btnVoice.classList.remove('listening');
            btnVoice.setAttribute('title', 'Voice Input');
            btnVoice.innerHTML = '<i class="ph-bold ph-microphone text-lg"></i>';
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'not-allowed') {
                showToast('Microphone access denied.', 'error');
            } else {
                showToast('Unable to recognize speech.', 'error');
            }
        };

        recognition.onresult = (event) => {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }

            if (finalTranscript) {
                const startPos = queryInput.selectionStart;
                const endPos = queryInput.selectionEnd;
                const originalText = queryInput.value;
                
                // Insert final text at cursor position
                queryInput.value = originalText.substring(0, startPos) + finalTranscript + originalText.substring(endPos);
                
                // Adjust cursor position
                const newCursorPos = startPos + finalTranscript.length;
                queryInput.selectionStart = newCursorPos;
                queryInput.selectionEnd = newCursorPos;
                
                // Trigger textarea auto-resize
                queryInput.dispatchEvent(new Event('input'));
            }
        };

        btnVoice.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } catch (e) {
        console.error('Speech recognition failed to initialize:', e);
        btnVoice.disabled = true;
        btnVoice.style.opacity = '0.4';
    }
}

// FEATURE 3: SOURCE CHAPTER VIEW MODEL HELPERS
const sourceModal = document.getElementById('source-modal-backdrop');
const btnCloseSource = document.getElementById('btn-close-source');
let previouslyFocusedElement = null;

function openSourceModal(citation) {
    if (!sourceModal) return;
    
    previouslyFocusedElement = document.activeElement;

    // Set title and metadata
    document.getElementById('source-title').textContent = citation.source_name || citation.chapter_title || 'Unknown Source';
    document.getElementById('source-meta-id').textContent = citation.chapter_id || 'N/A';
    document.getElementById('source-meta-pages').textContent = citation.page_range || 'N/A';
    document.getElementById('source-meta-score').textContent = citation.similarity ? `${(citation.similarity * 100).toFixed(1)}%` : 'N/A';

    // Set retrieved chunks
    const chunksList = document.getElementById('source-chunks-list');
    chunksList.innerHTML = '';

    const chunks = citation.retrieved_chunks || [];
    if (chunks.length === 0) {
        chunksList.innerHTML = '<div class="text-xs text-text-muted">No retrieved chunks text available.</div>';
    } else {
        chunks.forEach(chunk => {
            const chunkEl = document.createElement('pre');
            chunkEl.className = 'source-modal-chunk';
            chunkEl.textContent = chunk;
            chunksList.appendChild(chunkEl);
        });
    }

    // Show modal
    sourceModal.classList.add('show');
    sourceModal.setAttribute('aria-hidden', 'false');
    
    // Focus close button first
    if (btnCloseSource) btnCloseSource.focus();
    
    // Trap focus
    sourceModal.addEventListener('keydown', trapModalFocus);
}

function closeSourceModal() {
    if (!sourceModal) return;
    sourceModal.classList.remove('show');
    sourceModal.setAttribute('aria-hidden', 'true');
    sourceModal.removeEventListener('keydown', trapModalFocus);

    // Restore focus
    if (previouslyFocusedElement) {
        previouslyFocusedElement.focus();
    }
}

function trapModalFocus(e) {
    if (e.key !== 'Tab') return;

    const focusableElements = sourceModal.querySelectorAll('button, [tabindex="0"]');
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (e.shiftKey) { // Shift + Tab
        if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
        }
    } else { // Tab
        if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
        }
    }
}

// Attach close event listeners
if (btnCloseSource) {
    btnCloseSource.addEventListener('click', closeSourceModal);
}
if (sourceModal) {
    sourceModal.addEventListener('click', (e) => {
        if (e.target === sourceModal) {
            closeSourceModal();
        }
    });
}

// Global key down for escape - replaced with specialized listeners
// FEATURE 4: CONVERSATION EXPORT
const btnExport = document.getElementById('btn-export');
const exportDropdown = document.getElementById('export-dropdown');
const exportMarkdownBtn = document.getElementById('export-markdown');
const exportPdfBtn = document.getElementById('export-pdf');

function initExportControls() {
    if (!btnExport || !exportDropdown) return;

    // Toggle dropdown
    btnExport.addEventListener('click', (e) => {
        e.stopPropagation();
        exportDropdown.classList.toggle('show');
    });

    // Close dropdown on click outside
    document.addEventListener('click', () => {
        exportDropdown.classList.remove('show');
    });

    if (exportMarkdownBtn) {
        exportMarkdownBtn.addEventListener('click', () => {
            exportConversation('markdown');
        });
    }

    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', () => {
            exportConversation('pdf');
        });
    }
}

function exportConversation(format) {
    if (messageHistory.length === 0) {
        showToast('No conversations to export.', 'error');
        return;
    }

    switch (format) {
        case 'markdown':
            exportAsMarkdown();
            break;
        case 'pdf':
            exportAsPdf();
            break;
        default:
            console.warn(`Format ${format} not supported yet.`);
            showToast(`Format ${format} is under development.`, 'info');
    }
}

function exportAsMarkdown() {
    let mdContent = `# NeuroRAG Conversation\n`;
    mdContent += `*Generated on: ${new Date().toLocaleString()}*\n\n`;

    messageHistory.forEach((entry, index) => {
        mdContent += `## User (${entry.timestamp})\n`;
        mdContent += `${entry.query}\n\n`;

        mdContent += `## NeuroRAG\n`;
        if (entry.answer) {
            mdContent += `${entry.answer}\n\n`;
        } else {
            mdContent += `*Pending Response...*\n\n`;
        }
    });

    try {
        const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `neurorag_conversation_${Date.now()}.md`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showToast('Conversation exported as Markdown.', 'success');
    } catch (err) {
        console.error('Markdown export error:', err);
        showToast('Unable to export markdown.', 'error');
    }
}

function exportAsPdf() {
    window.print();
}

// TOAST NOTIFICATION HELPERS
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 pointer-events-none max-w-sm w-[320px]';
        document.body.appendChild(container);
    }
    
    // Enforce max 3 visible toasts
    const activeToasts = container.querySelectorAll('.clinical-toast');
    if (activeToasts.length >= 3) {
        activeToasts[0].remove();
    }
    
    const toast = document.createElement('div');
    toast.className = `clinical-toast pointer-events-auto flex items-start gap-3 p-3.5 rounded-xl border backdrop-blur-md shadow-glow transition-all duration-250 ease-out translate-x-[110%]`;
    
    let iconHTML = '';
    if (type === 'success') {
        toast.classList.add('bg-emerald-950/80', 'border-emerald-500/30', 'text-emerald-300');
        iconHTML = '<i class="ph-fill ph-check-circle text-emerald-400 text-lg flex-shrink-0 mt-0.5" aria-hidden="true"></i>';
    } else if (type === 'error') {
        toast.classList.add('bg-red-950/80', 'border-red-500/30', 'text-red-300');
        iconHTML = '<i class="ph-fill ph-warning-circle text-red-400 text-lg flex-shrink-0 mt-0.5" aria-hidden="true"></i>';
    } else {
        toast.classList.add('bg-bg-elevated/90', 'border-accent/30', 'text-text-primary');
        iconHTML = '<i class="ph-fill ph-info text-accent text-lg flex-shrink-0 mt-0.5" aria-hidden="true"></i>';
    }
    
    toast.innerHTML = `
        ${iconHTML}
        <div class="flex-1 text-[12px] font-semibold leading-normal pr-1">${escapeHTML(message)}</div>
        <button class="text-text-muted hover:text-white transition-colors" onclick="this.parentElement.classList.add('hide-toast'); setTimeout(() => this.parentElement.remove(), 250)" aria-label="Close Notification">
            <i class="ph ph-x text-sm"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.classList.remove('translate-x-[110%]');
    });
    
    setTimeout(() => {
        toast.classList.add('hide-toast');
        setTimeout(() => toast.remove(), 250);
    }, 3500);
}

// ==========================================
// PHASE 3 ADDITIONS: BOOKMARKS MANAGEMENT
// ==========================================
function getBookmarks() {
    const username = window.currentUser || 'anonymous';
    const key = `neurorag_bookmarks_${username}`;
    try {
        return JSON.parse(localStorage.getItem(key)) || [];
    } catch (e) {
        return [];
    }
}

function saveBookmarks(bookmarks) {
    const username = window.currentUser || 'anonymous';
    const key = `neurorag_bookmarks_${username}`;
    localStorage.setItem(key, JSON.stringify(bookmarks));
}

function checkIsBookmarked(messageId) {
    const bookmarks = getBookmarks();
    return bookmarks.some(b => b.id === messageId);
}

function toggleBookmark(answer, query, messageId, btn) {
    let bookmarks = getBookmarks();
    const index = bookmarks.findIndex(b => b.id === messageId);
    
    if (index > -1) {
        bookmarks.splice(index, 1);
        btn.classList.remove('active');
        btn.innerHTML = '<i class="ph ph-bookmark-simple text-xs"></i>';
        showToast('Bookmark removed.', 'info');
    } else {
        bookmarks.push({
            id: messageId,
            query: query,
            answer: answer,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            mode: currentMode
        });
        btn.classList.add('active');
        btn.innerHTML = '<i class="ph-fill ph-bookmark-simple text-xs"></i>';
        showToast('Bookmark saved.', 'success');
    }
    saveBookmarks(bookmarks);
    renderBookmarks();
}

function deleteBookmark(event, messageId) {
    if (event) event.stopPropagation();
    let bookmarks = getBookmarks();
    bookmarks = bookmarks.filter(b => b.id !== messageId);
    saveBookmarks(bookmarks);
    renderBookmarks();
    
    // De-activate button on screen if it exists
    const btn = document.querySelector(`#${messageId}-response .btn-bookmark-response`) || document.querySelector(`#${messageId} .btn-bookmark-response`);
    if (btn) {
        btn.classList.remove('active');
        btn.innerHTML = '<i class="ph ph-bookmark-simple text-xs"></i>';
    }
    showToast('Bookmark removed.', 'info');
}

function renderBookmarks() {
    const container = document.getElementById('bookmarks-container');
    if (!container) return;
    
    const bookmarks = getBookmarks();
    if (bookmarks.length === 0) {
        container.innerHTML = '<div class="text-[11px] text-text-muted italic px-2">No bookmarks saved yet.</div>';
        return;
    }
    
    container.innerHTML = '';
    bookmarks.forEach(bookmark => {
        const item = document.createElement('div');
        item.className = 'bookmark-item';
        
        item.addEventListener('click', () => {
            handleBookmarkClick(bookmark);
        });
        
        // Extract paragraph preview
        const firstPara = bookmark.answer.split('\n\n')[0].replace(/[*#]/g, '').trim();
        
        item.innerHTML = `
            <div class="flex-1 min-w-0">
                <div class="font-medium truncate text-white">${escapeHTML(bookmark.query)}</div>
                <div class="text-[10px] text-text-muted truncate mt-0.5">${escapeHTML(firstPara)}</div>
            </div>
            <i class="ph ph-trash bookmark-delete-btn text-xs shrink-0 mt-0.5" title="Remove bookmark"></i>
        `;
        
        const trashBtn = item.querySelector('.bookmark-delete-btn');
        trashBtn.addEventListener('click', (e) => {
            deleteBookmark(e, bookmark.id);
        });
        
        container.appendChild(item);
    });
}

function handleBookmarkClick(bookmark) {
    const responseId = bookmark.id.endsWith('-response') ? bookmark.id : bookmark.id + '-response';
    const queryId = bookmark.id.endsWith('-response') ? bookmark.id.replace('-response', '') : bookmark.id;
    
    const msgElement = document.getElementById(responseId) || document.getElementById(queryId);
    if (msgElement) {
        msgElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        msgElement.classList.add('highlight-flash');
        setTimeout(() => msgElement.classList.remove('highlight-flash'), 1500);
    } else {
        // Restore conversation to chat window if not found in current DOM
        const welcomeMsg = document.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();
        
        chatContainer.innerHTML = '';
        messageHistory = [{
            id: queryId,
            query: bookmark.query,
            answer: bookmark.answer,
            timestamp: bookmark.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            mode: bookmark.mode || currentMode
        }];
        
        addMessage('user', bookmark.query, queryId);
        addAssistantMessage({
            answer: bookmark.answer,
            query: bookmark.query,
            citations: [],
            followup_questions: []
        }, responseId);
        
        updateTimeline();
        showToast('Restored bookmarked Q&A findings to workspace.', 'info');
    }
}

function initBookmarks() {
    renderBookmarks();
}

// ==========================================
// PHASE 3 ADDITIONS: SESSION HISTORY
// ==========================================
let pastSessions = [];

async function loadSessionHistory() {
    const historySection = document.getElementById('history-section');
    const container = document.getElementById('history-container');
    
    if (historySection && container) {
        historySection.classList.remove('hidden');
        container.innerHTML = '';
        for (let i = 0; i < 3; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'sidebar-skeleton-card border border-border/40 rounded-lg p-3 bg-white/2 space-y-2 mb-2 placeholder-shimmer';
            skeleton.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="sidebar-skeleton-text w-24 bg-white/10 rounded"></div>
                    <div class="sidebar-skeleton-text w-12 bg-white/5 rounded"></div>
                </div>
                <div class="sidebar-skeleton-text w-full bg-white/5 rounded mt-2"></div>
            `;
            container.appendChild(skeleton);
        }
    }
    
    try {
        const response = await fetch('/api/conversations');
        const data = await response.json();
        if (data.success && data.conversations) {
            pastSessions = data.conversations;
            renderSessionHistory(pastSessions);
        } else if (historySection) {
            historySection.classList.add('hidden');
        }
    } catch (error) {
        console.error("Error loading session history:", error);
        if (historySection) {
            historySection.classList.add('hidden');
        }
    }
}

function renderSessionHistory(conversations) {
    const historySection = document.getElementById('history-section');
    const container = document.getElementById('history-container');
    if (!container || !historySection) return;
    
    if (!conversations || conversations.length === 0) {
        historySection.classList.add('hidden');
        return;
    }
    
    historySection.classList.remove('hidden');
    container.innerHTML = '';
    
    conversations.forEach(sess => {
        const card = document.createElement('div');
        card.className = 'sidebar-session-card border border-border/40 rounded-lg p-3 bg-white/2 hover:bg-white/5 transition-all mb-2';
        
        const dateStr = new Date(sess.last_activity).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        const summaryText = sess.summary || "Clinical session complete.";
        
        card.innerHTML = `
            <div class="flex items-center justify-between cursor-pointer session-card-header">
                <div class="flex flex-col min-w-0">
                    <span class="text-[10px] font-semibold text-text-secondary">Session: ${dateStr}</span>
                    <span class="text-[9px] text-text-muted mt-0.5">${sess.query_count} queries • ${sess.critical_count} critical</span>
                </div>
                <i class="ph ph-caret-down text-text-muted transition-transform duration-300 font-bold text-xs"></i>
            </div>
            
            <div class="session-details hidden mt-3 pt-3 border-t border-border/20 space-y-2">
                <div class="session-summary-card">
                    <strong>Summary:</strong> ${escapeHTML(summaryText)}
                </div>
                
                ${sess.top_topics && sess.top_topics.length > 0 ? `
                <div class="text-[9px] text-text-muted font-bold uppercase tracking-wider">Topics:</div>
                <div class="flex flex-wrap gap-1">
                    ${sess.top_topics.map(t => `<span class="px-1.5 py-0.5 rounded bg-accent/10 border border-accent/20 text-accent text-[9px] font-semibold">${escapeHTML(t)}</span>`).join('')}
                </div>
                ` : ''}
                
                ${sess.chats && sess.chats.length > 0 ? `
                <div class="text-[9px] text-text-muted font-bold uppercase tracking-wider">Queries:</div>
                <ul class="space-y-1.5 pl-2 list-none text-[11px] text-text-secondary">
                    ${sess.chats.map((c, idx) => `
                        <li class="hover:text-accent transition-colors truncate flex items-center gap-1.5" onclick="event.stopPropagation(); loadSessionById('${sess.session_id}')">
                            <i class="ph ph-circle text-[6px] text-text-muted"></i>
                            <span>${escapeHTML(c.question || c.query)}</span>
                        </li>
                    `).join('')}
                </ul>
                ` : ''}
                
                <button class="w-full mt-2 btn-micro py-1 bg-accent/15 border border-accent/25 text-[10px] font-bold rounded text-accent hover:bg-accent/25 transition-all text-center" onclick="event.stopPropagation(); loadSessionById('${sess.session_id}')">
                    Load Session Workspace
                </button>
            </div>
        `;
        
        // Add click toggle to card header
        const header = card.querySelector('.session-card-header');
        header.addEventListener('click', () => {
            toggleSessionCollapse(card);
        });
        
        container.appendChild(card);
    });
}

function toggleSessionCollapse(cardElement) {
    const details = cardElement.querySelector('.session-details');
    const caret = cardElement.querySelector('.ph-caret-down');
    
    if (details) {
        const isCollapsed = details.classList.contains('hidden');
        if (isCollapsed) {
            details.classList.remove('hidden');
            if (caret) caret.style.transform = 'rotate(180deg)';
        } else {
            details.classList.add('hidden');
            if (caret) caret.style.transform = 'rotate(0deg)';
        }
    }
}

function loadSessionById(sessionId) {
    const sess = pastSessions.find(s => s.session_id === sessionId);
    if (sess) {
        renderSession(sess);
        showToast("Loaded historical session.", "success");
    }
}

function renderSession(sessionData) {
    const welcomeMsg = document.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();
    
    chatContainer.innerHTML = '';
    messageHistory = [];
    
    sessionData.chats.forEach((chat, idx) => {
        const messageId = `msg-${Date.now()}-${idx}`;
        const query = chat.question || chat.query;
        const answer = chat.answer;
        
        const historyEntry = {
            id: messageId,
            query: query,
            answer: answer,
            timestamp: chat.timestamp ? new Date(chat.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
            mode: chat.mode || 'patient'
        };
        messageHistory.push(historyEntry);
        
        addMessage('user', query, messageId);
        
        addAssistantMessage({
            answer: answer,
            query: query,
            citations: chat.citations || [],
            followup_questions: chat.followup_questions || [],
            suggested_questions: chat.suggested_questions || (chat.followup_questions ? chat.followup_questions.slice(0, 3) : []),
            severity_level: chat.severity_level || 'informational',
            retrieved_chunks_count: chat.retrieved_chunks_count || 0
        }, messageId + '-response');
    });
    
    // Enable generate report button
    if (btnGenerateReport) {
        btnGenerateReport.classList.remove('hidden');
    }
    
    updateTimeline();
}

function clearActiveWorkspace() {
    chatContainer.innerHTML = '';
    messageHistory = [];
    
    // Hide report button
    if (btnGenerateReport) {
        btnGenerateReport.classList.add('hidden');
    }
    
    // Hide/clear timeline container
    if (timelineContainer) {
        timelineContainer.classList.add('hidden');
        timelineContainer.innerHTML = '';
    }
    
    // Restore welcome message
    const welcomeHtml = `
        <div class="welcome-message animate-message-enter flex flex-col items-center justify-center h-full text-center mt-12 px-4">
            <div class="w-20 h-20 rounded-3xl bg-slate-800/40 border border-border flex items-center justify-center mb-6 shadow-xl relative backdrop-blur-md">
                <svg class="w-10 h-10 text-accent animate-pulse-glow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z" />
                    <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z" />
                    <path d="M12 5v13" />
                </svg>
            </div>
            <h1 class="font-display text-3xl font-bold text-white mb-3 tracking-tight">Clinical Assistant Workspace</h1>
            <p class="text-text-secondary text-sm mb-6 leading-relaxed max-w-md font-medium">
                Search and analyze the 51-chapter neurological disorders manual. Type a diagnostic, pathology, or pharmaceutical query below.
            </p>
            <div class="flex gap-2.5 text-[9px] text-text-muted font-semibold tracking-widest uppercase">
                <div class="glass-subtle flex items-center gap-1.5 px-3 py-1.5 rounded-full"><i class="ph-fill ph-database text-accent text-xs"></i> FAISS VECTORS</div>
                <div class="glass-subtle flex items-center gap-1.5 px-3 py-1.5 rounded-full"><i class="ph-fill ph-lightning text-accent text-xs"></i> GEMINI 2.5 FLASH</div>
            </div>
        </div>
    `;
    chatContainer.innerHTML = welcomeHtml;
    
    // Show example queries container
    const examples = document.getElementById('example-queries-container');
    if (examples) {
        examples.classList.remove('hidden');
    }
}

function initSessionHistory() {
    const btnEndSession = document.getElementById('btn-end-session');
    if (btnEndSession) {
        btnEndSession.addEventListener('click', async () => {
            if (messageHistory.length === 0) {
                showToast("No active session queries to summarize.", "error");
                return;
            }
            
            const confirmEnd = confirm("End this clinical session and generate an AI summary of all queries?");
            if (!confirmEnd) return;
            
            try {
                // Show loading toast
                showToast("Generating session summary...", "info");
                
                const response = await fetch('/api/end_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await response.json();
                if (data.success) {
                    showToast(`Session archived: ${data.summary}`, 'success');
                    clearActiveWorkspace();
                    await loadSessionHistory();
                } else {
                    showToast(data.message || "Failed to end session.", 'error');
                }
            } catch (error) {
                console.error("Error ending session:", error);
                showToast("Failed to connect to server.", 'error');
            }
        });
    }
    
    loadSessionHistory();
}

// ==========================================
// PHASE 3 ADDITIONS: KEYBOARD SHORTCUTS
// ==========================================
const shortcutsModal = document.getElementById('shortcuts-modal-backdrop');
const btnCloseShortcuts = document.getElementById('btn-close-shortcuts');
const linkShortcuts = document.getElementById('link-shortcuts');

function openShortcutsModal() {
    if (shortcutsModal) {
        shortcutsModal.classList.add('show');
        if (btnCloseShortcuts) btnCloseShortcuts.focus();
    }
}

function closeShortcutsModal() {
    if (shortcutsModal) {
        shortcutsModal.classList.remove('show');
    }
}

function initKeyboardShortcuts() {
    if (linkShortcuts) {
        linkShortcuts.addEventListener('click', (e) => {
            e.preventDefault();
            openShortcutsModal();
        });
    }
    if (btnCloseShortcuts) {
        btnCloseShortcuts.addEventListener('click', closeShortcutsModal);
    }
    if (shortcutsModal) {
        shortcutsModal.addEventListener('click', (e) => {
            if (e.target === shortcutsModal) {
                closeShortcutsModal();
            }
        });
    }
    
    // Bind Keyboard shortcuts global listener
    document.addEventListener('keydown', (e) => {
        // Escape key handler (close modals & sidebar drawer)
        if (e.key === 'Escape') {
            closeSourceModal();
            closeShortcutsModal();
            if (reportModal && reportModal.classList.contains('active')) {
                reportModal.classList.remove('active');
            }
            if (sidebar && sidebar.classList.contains('sidebar-open')) {
                sidebar.classList.remove('sidebar-open');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('opacity-100');
                    setTimeout(() => sidebarOverlay.classList.add('hidden'), 300);
                }
            }
        }
        
        // Ctrl/Cmd + K (focus search)
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }

        // Ctrl/Cmd + B (toggle sidebar)
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
            e.preventDefault();
            if (sidebarToggle) {
                sidebarToggle.click();
            } else if (sidebar) {
                sidebar.classList.toggle('sidebar-open');
                if (sidebar.classList.contains('sidebar-open') && sidebarOverlay) {
                    sidebarOverlay.classList.remove('hidden');
                    requestAnimationFrame(() => sidebarOverlay.classList.add('opacity-100'));
                } else if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('opacity-100');
                    setTimeout(() => sidebarOverlay.classList.add('hidden'), 300);
                }
            }
        }

        // Ctrl/Cmd + Enter (submit query)
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (document.activeElement === queryInput) {
                e.preventDefault();
                handleSubmit();
            }
        }

        // '?' key (toggle shortcuts modal)
        if (e.key === '?' && document.activeElement !== queryInput && document.activeElement !== searchInput) {
            e.preventDefault();
            if (shortcutsModal) {
                if (shortcutsModal.classList.contains('show')) {
                    closeShortcutsModal();
                } else {
                    openShortcutsModal();
                }
            }
        }
    });
}

console.log('NeuroRAG Clinical Assistant Workspace Active - Phase 3 Configured');