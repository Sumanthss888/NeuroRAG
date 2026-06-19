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

// Sidebar History Real-time Search Filter
if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase().trim();
        const items = timelineContainer.querySelectorAll('.timeline-item');
        items.forEach((item, idx) => {
            if (idx < messageHistory.length) {
                const queryText = messageHistory[idx].query.toLowerCase();
                if (queryText.includes(term)) {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            }
        });
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
            addErrorMessage(data.error || 'An error occurred while processing your query');
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
    messageCard.className = `glass-subtle relative w-full rounded-[4px_18px_18px_18px] p-[12px_16px] border border-border shadow-soft`;
    
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
    
    const suggestions = data.followup_questions && data.followup_questions.length > 0 
        ? data.followup_questions 
        : generateFallbackSuggestions(messageHistory[messageHistory.length - 1].query);
        
    const followupSection = createFollowupSection(suggestions);
    contentContainer.appendChild(followupSection);
    
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

function addErrorMessage(errorText) {
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'flex w-full animate-message-enter pr-12 justify-start';
    
    const messageCard = document.createElement('div');
    messageCard.className = 'glass-panel relative w-full rounded-2xl rounded-tl-sm p-6';
    
    messageCard.innerHTML = `
        <div class="absolute bottom-6 left-0 top-6 w-1 rounded-r-full bg-red-500/80"></div>
        <div class="pl-4">
            <div class="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-widest text-red-400">
                <i class="ph-fill ph-warning-circle text-lg"></i> System Error
            </div>
            <p class="text-[14px] font-medium text-slate-300 leading-relaxed">${errorText}</p>
        </div>
    `;
    
    messageWrapper.appendChild(messageCard);
    chatContainer.appendChild(messageWrapper);
    scrollToBottom();
}

function showLoading() {
    const loadingId = 'loading-' + Date.now();
    const messageWrapper = document.createElement('div');
    messageWrapper.id = loadingId;
    messageWrapper.className = 'flex w-full animate-message-enter pr-12 justify-start';
    
    const isPatient = currentMode === 'patient';
    const accentColor = isPatient ? 'accent' : 'emerald';
    
    const messageCard = document.createElement('div');
    messageCard.className = 'glass-subtle relative w-64 rounded-2xl rounded-tl-sm p-5 flex items-center justify-center border border-border';
    
    messageCard.innerHTML = `
        <div class="flex flex-col items-center justify-center gap-3 py-2">
            <div class="neural-pulse-container text-${accentColor}">
                <div class="neural-wave"></div>
                <div class="neural-wave"></div>
                <div class="neural-wave"></div>
                <div class="neural-wave"></div>
            </div>
            <div class="text-[10px] font-semibold uppercase tracking-widest text-text-muted">Analyzing clinical context...</div>
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

console.log('NeuroRAG Clinical Assistant Workspace Active');