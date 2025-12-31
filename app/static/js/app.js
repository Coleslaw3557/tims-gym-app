// Gym Tracker App

const API = {
    async get(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    },
    async post(url, data) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    },
    async patch(url, data) {
        const res = await fetch(url, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    },
    async delete(url) {
        const res = await fetch(url, { method: 'DELETE' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    }
};

// State
let state = {
    currentView: 'home',
    activeSession: null,
    program: null,
    previousWeights: {},
    completedSets: new Set(),
    // Gallery state
    galleryImages: [],
    galleryIndex: 0,
    galleryExerciseName: '',
    // Confirm dialog state
    confirmCallback: null
};

// DOM Elements
const views = {
    home: document.getElementById('home-view'),
    workout: document.getElementById('workout-view'),
    history: document.getElementById('history-view'),
    stats: document.getElementById('stats-view'),
    sessionDetail: document.getElementById('session-detail-view'),
    exerciseHistory: document.getElementById('exercise-history-view')
};

// Navigation
document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const view = tab.dataset.view;
        showView(view);
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
    });
});

function showView(viewName) {
    Object.values(views).forEach(v => v.classList.remove('active'));
    views[viewName]?.classList.add('active');
    state.currentView = viewName;

    if (viewName === 'home') loadHome();
    if (viewName === 'history') loadHistory();
    if (viewName === 'stats') loadStats();
}

// Home View
async function loadHome() {
    try {
        const session = await API.get('/api/sessions/active');
        const banner = document.getElementById('active-session-banner');

        if (session) {
            state.activeSession = session;
            banner.classList.remove('hidden');
        } else {
            banner.classList.add('hidden');
        }
    } catch (e) {
        console.error('Error loading home:', e);
    }
}

// Day selection
document.querySelectorAll('.day-card').forEach(card => {
    card.addEventListener('click', () => startWorkout(parseInt(card.dataset.day)));
});

document.getElementById('continue-workout-btn').addEventListener('click', () => {
    if (state.activeSession) {
        loadWorkout(state.activeSession);
    }
});

// Start new workout
async function startWorkout(day) {
    try {
        // Check for active session first
        const active = await API.get('/api/sessions/active');
        if (active) {
            const dayNames = { 1: 'Lower Body', 2: 'Upper Push', 3: 'Upper Pull' };
            showConfirmDialog(
                'Active Workout',
                `You have an active Day ${active.day_type} (${dayNames[active.day_type]}) workout. What would you like to do?`,
                [
                    { label: 'Continue Current', action: () => loadWorkout(active), primary: true },
                    { label: 'Cancel & Start New', action: async () => {
                        await API.delete(`/api/sessions/${active.id}`);
                        const session = await API.post('/api/sessions', { day_type: day });
                        state.activeSession = session;
                        loadWorkout(session);
                    }, danger: true }
                ]
            );
            return;
        }

        const session = await API.post('/api/sessions', { day_type: day });
        state.activeSession = session;
        loadWorkout(session);
    } catch (e) {
        console.error('Error starting workout:', e);
        alert('Failed to start workout');
    }
}

// Load workout view
async function loadWorkout(session) {
    state.activeSession = session;
    state.completedSets = new Set();

    // Mark already completed sets
    session.set_logs.forEach(log => {
        if (log.completed_at) {
            state.completedSets.add(`${log.exercise_id}-${log.set_number}`);
        }
    });

    // Get program for this day
    const dayProgram = await API.get(`/api/program/day/${session.day_type}`);
    state.program = dayProgram;

    // Get previous weights and PRs in parallel
    try {
        const [prevWeights, prData] = await Promise.all([
            API.get(`/api/sessions/${session.id}/previous-weights`),
            API.get('/api/stats/prs')
        ]);
        state.previousWeights = {};
        prevWeights.forEach(pw => {
            state.previousWeights[pw.exercise_id] = pw.weights;
        });
        state.prs = {};
        prData.prs.forEach(pr => {
            state.prs[pr.exercise_id] = { weight: pr.weight, reps: pr.reps };
        });
    } catch (e) {
        state.previousWeights = {};
        state.prs = {};
    }

    document.getElementById('workout-title').textContent = `Day ${session.day_type}: ${session.day_name}`;
    renderExercises(dayProgram.exercises, session.set_logs);

    showView('workout');
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
}

// Format form notes into bullet points
function formatFormNotes(notes) {
    if (!notes) return '';
    // Split by newlines and filter empty lines
    const lines = notes.split('\n').filter(line => line.trim());
    if (lines.length === 0) return '';
    return `<ul class="form-notes-list">${lines.map(line => `<li>${line.trim()}</li>`).join('')}</ul>`;
}

// Render exercises
function renderExercises(exercises, setLogs) {
    const container = document.getElementById('exercises-container');
    container.innerHTML = '';

    exercises.forEach((pe, idx) => {
        const ex = pe.exercise;
        const repsDisplay = pe.reps_max ? `${pe.reps_min}-${pe.reps_max}` : pe.reps_min;

        // Get logged sets for this exercise
        const exerciseLogs = setLogs.filter(l => l.exercise_id === ex.id);

        // Get previous weights for this exercise
        const prevWeights = state.previousWeights[ex.id] || [];

        // Get PR and calculate last session's max weight
        const pr = state.prs[ex.id];
        const lastMaxWeight = prevWeights.length > 0 ? Math.max(...prevWeights.filter(w => w)) : null;

        // Use original image_url as thumbnail
        const thumbnailImage = ex.image_url;
        // GIF for the expanded detail view
        const gifUrl = ex.gif_url;
        // Check if exercise has gallery images
        const hasImages = ex.images && ex.images.length > 0;

        // Check if this is a mobility exercise
        const isMobility = ex.category === 'mobility';

        // Build weight hints for header (only for strength exercises)
        let weightHints = '';
        if (!isMobility && (pr || lastMaxWeight)) {
            const hints = [];
            if (pr) hints.push(`PR: ${pr.weight} lbs`);
            if (lastMaxWeight) hints.push(`Last: ${lastMaxWeight} lbs`);
            weightHints = `<div class="exercise-weight-hints">${hints.join(' · ')}</div>`;
        }

        const card = document.createElement('div');
        card.className = 'exercise-card';
        card.innerHTML = `
            <div class="exercise-header" data-exercise-id="${ex.id}">
                ${thumbnailImage
                    ? `<img src="${thumbnailImage}" alt="${ex.name}" class="exercise-image ${hasImages ? 'exercise-image-clickable' : ''}" loading="lazy" data-exercise-id="${ex.id}" data-has-gallery="${hasImages}">`
                    : `<div class="exercise-image-placeholder">No image</div>`
                }
                <div class="exercise-info">
                    <div class="exercise-name">${ex.name}</div>
                    <div class="exercise-meta">${pe.sets} x ${repsDisplay}</div>
                    ${weightHints}
                </div>
            </div>
            <div class="exercise-details" id="details-${ex.id}">
                ${gifUrl ? `
                    <div class="exercise-gif-container">
                        <img src="${gifUrl}" alt="${ex.name} demonstration" class="exercise-gif-large" loading="lazy">
                    </div>
                ` : ''}
                ${ex.form_notes ? `
                    <div class="form-notes-section">
                        <div class="form-notes-header">Form</div>
                        ${formatFormNotes(ex.form_notes)}
                    </div>
                ` : (ex.description ? `<p class="exercise-description">${ex.description}</p>` : '')}
                ${pe.notes ? `<div class="exercise-notes">${pe.notes}</div>` : ''}
                <div class="sets-container ${isMobility ? 'mobility-sets' : ''}">
                    <div class="sets-header">
                        <div>Set</div>
                        ${isMobility ? '<div>Duration</div>' : '<div>Weight</div>'}
                        <div>${isMobility ? '' : 'Reps'}</div>
                        <div></div>
                    </div>
                    ${Array.from({ length: pe.sets }, (_, i) => {
                        const setNum = i + 1;
                        const log = exerciseLogs.find(l => l.set_number === setNum);
                        const prevWeight = prevWeights[i] || '';
                        const isCompleted = state.completedSets.has(`${ex.id}-${setNum}`);

                        if (isMobility) {
                            // Mobility exercise: show duration/reps field and simple completion
                            return `
                                <div class="set-row mobility-row" data-exercise-id="${ex.id}" data-set="${setNum}" data-mobility="true">
                                    <div class="set-number">${setNum}</div>
                                    <input type="number" class="set-input reps-input ${isCompleted ? 'completed' : ''}"
                                           value="${log?.reps_completed ?? pe.reps_min}"
                                           placeholder="${pe.reps_min}${pe.notes?.includes('sec') ? 's' : ''}"
                                           inputmode="numeric"
                                           data-exercise-id="${ex.id}"
                                           data-set="${setNum}">
                                    <div></div>
                                    <button class="complete-set-btn ${isCompleted ? 'completed' : ''}"
                                            data-exercise-id="${ex.id}"
                                            data-set="${setNum}"
                                            data-mobility="true">
                                        ${isCompleted ? '&#10003;' : '&#10003;'}
                                    </button>
                                </div>
                            `;
                        } else {
                            // Strength exercise: show weight and reps
                            return `
                                <div class="set-row" data-exercise-id="${ex.id}" data-set="${setNum}">
                                    <div class="set-number">${setNum}</div>
                                    <input type="number" class="set-input weight-input ${isCompleted ? 'completed' : ''}"
                                           value="${log?.weight ?? prevWeight}"
                                           placeholder="${prevWeight || 'lbs'}"
                                           inputmode="decimal"
                                           data-exercise-id="${ex.id}"
                                           data-set="${setNum}">
                                    <input type="number" class="set-input reps-input ${isCompleted ? 'completed' : ''}"
                                           value="${log?.reps_completed ?? pe.reps_min}"
                                           placeholder="${pe.reps_min}"
                                           inputmode="numeric"
                                           data-exercise-id="${ex.id}"
                                           data-set="${setNum}">
                                    <button class="complete-set-btn ${isCompleted ? 'completed' : ''}"
                                            data-exercise-id="${ex.id}"
                                            data-set="${setNum}">
                                        ${isCompleted ? '&#10003;' : '&#10003;'}
                                    </button>
                                </div>
                            `;
                        }
                    }).join('')}
                </div>
            </div>
        `;

        container.appendChild(card);
    });

    // Expand first exercise by default
    if (exercises.length > 0) {
        document.getElementById(`details-${exercises[0].exercise.id}`).classList.add('expanded');
    }

    // Event listeners for exercise headers (expand/collapse)
    container.querySelectorAll('.exercise-header').forEach(header => {
        header.addEventListener('click', (e) => {
            // Don't toggle if clicking on image with gallery
            if (e.target.classList.contains('exercise-image-clickable')) return;
            const exId = header.dataset.exerciseId;
            document.querySelectorAll('.exercise-details').forEach(d => {
                if (d.id === `details-${exId}`) {
                    d.classList.toggle('expanded');
                }
            });
        });
    });

    // Event listeners for clickable images (open gallery)
    container.querySelectorAll('.exercise-image-clickable').forEach(img => {
        img.addEventListener('click', (e) => {
            e.stopPropagation();
            const exId = parseInt(img.dataset.exerciseId);
            const exercise = exercises.find(pe => pe.exercise.id === exId)?.exercise;
            if (exercise && exercise.images && exercise.images.length > 0) {
                openGallery(exercise.name, exercise.images);
            }
        });
    });

    // Event listeners for complete buttons
    container.querySelectorAll('.complete-set-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            completeSet(btn);
        });
    });
}

// Complete a set
async function completeSet(btn) {
    const exerciseId = parseInt(btn.dataset.exerciseId);
    const setNum = parseInt(btn.dataset.set);
    const row = btn.closest('.set-row');
    const isMobility = btn.dataset.mobility === 'true';
    const weightInput = row.querySelector('.weight-input');
    const repsInput = row.querySelector('.reps-input');

    const weight = weightInput ? (parseFloat(weightInput.value) || null) : null;
    const reps = parseInt(repsInput.value) || null;

    // Mobility exercises don't require weight
    if (!isMobility && !weight) {
        alert('Please enter weight');
        return;
    }
    if (!reps) {
        alert(isMobility ? 'Please enter duration/reps' : 'Please enter reps');
        return;
    }

    try {
        await API.post(`/api/sessions/${state.activeSession.id}/sets`, {
            exercise_id: exerciseId,
            set_number: setNum,
            weight: weight,
            reps_completed: reps
        });

        state.completedSets.add(`${exerciseId}-${setNum}`);
        btn.classList.add('completed');
        weightInput.classList.add('completed');
        repsInput.classList.add('completed');
    } catch (e) {
        console.error('Error logging set:', e);
        alert('Failed to log set');
    }
}

// Exit workout
document.getElementById('exit-workout-btn').addEventListener('click', () => {
    showView('home');
    document.querySelector('.nav-tab[data-view="home"]').classList.add('active');
});

// Finish workout
document.getElementById('finish-workout-btn').addEventListener('click', async () => {
    if (!confirm('Finish this workout?')) return;

    try {
        await API.post(`/api/sessions/${state.activeSession.id}/complete`);
        state.activeSession = null;
        showView('home');
        document.querySelector('.nav-tab[data-view="home"]').classList.add('active');
    } catch (e) {
        console.error('Error finishing workout:', e);
        alert('Failed to finish workout');
    }
});

// History View
async function loadHistory() {
    const container = document.getElementById('history-list');
    container.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const sessions = await API.get('/api/sessions?limit=50');

        if (sessions.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No workout history yet</p></div>';
            return;
        }

        const dayNames = { 1: 'Lower Body', 2: 'Upper Push', 3: 'Upper Pull' };

        container.innerHTML = sessions.map(s => {
            const date = new Date(s.date);
            const dateStr = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
            const duration = s.completed_at
                ? formatDuration(new Date(s.started_at), new Date(s.completed_at))
                : 'In progress';

            return `
                <div class="history-item" data-session-id="${s.id}">
                    <div class="history-date">${dateStr}</div>
                    <div class="history-day">Day ${s.day_type}: ${dayNames[s.day_type]}</div>
                    <div class="history-duration">${duration}</div>
                </div>
            `;
        }).join('');

        container.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => loadSessionDetail(parseInt(item.dataset.sessionId)));
        });
    } catch (e) {
        console.error('Error loading history:', e);
        container.innerHTML = '<div class="empty-state"><p>Failed to load history</p></div>';
    }
}

function formatDuration(start, end) {
    const mins = Math.round((end - start) / 60000);
    if (mins < 60) return `${mins} min`;
    const hrs = Math.floor(mins / 60);
    const remainMins = mins % 60;
    return `${hrs}h ${remainMins}m`;
}

// Session Detail
async function loadSessionDetail(sessionId) {
    try {
        const session = await API.get(`/api/sessions/${sessionId}`);
        const dayNames = { 1: 'Lower Body', 2: 'Upper Push', 3: 'Upper Pull' };

        const date = new Date(session.date);
        const dateStr = date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

        document.getElementById('session-detail-title').textContent = `Day ${session.day_type}: ${dayNames[session.day_type]}`;

        // Group sets by exercise
        const exerciseMap = {};
        session.set_logs.forEach(log => {
            if (!exerciseMap[log.exercise_id]) {
                exerciseMap[log.exercise_id] = [];
            }
            exerciseMap[log.exercise_id].push(log);
        });

        // Get exercise names
        const program = await API.get(`/api/program/day/${session.day_type}`);
        const exerciseNames = {};
        program.exercises.forEach(pe => {
            exerciseNames[pe.exercise.id] = pe.exercise.name;
        });

        const content = document.getElementById('session-detail-content');
        content.innerHTML = `
            <div class="session-summary">
                <div>${dateStr}</div>
                ${session.completed_at
                    ? `<div>Duration: ${formatDuration(new Date(session.started_at), new Date(session.completed_at))}</div>`
                    : '<div>In progress</div>'
                }
            </div>
            ${Object.entries(exerciseMap).map(([exId, sets]) => `
                <div class="session-exercise" data-exercise-id="${exId}">
                    <div class="session-exercise-name">${exerciseNames[exId] || 'Unknown Exercise'}</div>
                    ${sets.sort((a, b) => a.set_number - b.set_number).map(s => `
                        <div class="session-set">
                            <span>Set ${s.set_number}:</span>
                            <span>${s.weight || 0} lbs x ${s.reps_completed || 0} reps</span>
                        </div>
                    `).join('')}
                </div>
            `).join('')}
        `;

        // Make exercise names clickable
        content.querySelectorAll('.session-exercise').forEach(el => {
            el.style.cursor = 'pointer';
            el.addEventListener('click', () => loadExerciseHistory(parseInt(el.dataset.exerciseId)));
        });

        showView('sessionDetail');
    } catch (e) {
        console.error('Error loading session detail:', e);
        alert('Failed to load session details');
    }
}

document.getElementById('back-to-history-btn').addEventListener('click', () => {
    showView('history');
    document.querySelector('.nav-tab[data-view="history"]').classList.add('active');
});

// Exercise History
async function loadExerciseHistory(exerciseId) {
    try {
        const history = await API.get(`/api/exercises/${exerciseId}/history?limit=30`);

        document.getElementById('exercise-history-title').textContent = history.exercise.name;

        const content = document.getElementById('exercise-history-content');

        if (history.history.length === 0) {
            content.innerHTML = '<div class="empty-state"><p>No history for this exercise</p></div>';
        } else {
            content.innerHTML = `
                ${history.current_pr ? `<div class="pr-item"><span class="pr-exercise">Current PR</span><span class="pr-weight">${history.current_pr} lbs</span></div>` : ''}
                ${history.history.map(entry => {
                    const date = new Date(entry.date);
                    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                    return `
                        <div class="history-session">
                            <div class="history-session-date">${dateStr}</div>
                            <div class="history-session-sets">
                                ${entry.sets.map(s => `
                                    <span class="history-set-badge ${s.weight === history.current_pr ? 'pr' : ''}">
                                        ${s.weight || 0} x ${s.reps_completed || 0}
                                    </span>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }).join('')}
            `;
        }

        showView('exerciseHistory');
    } catch (e) {
        console.error('Error loading exercise history:', e);
        alert('Failed to load exercise history');
    }
}

document.getElementById('back-from-exercise-btn').addEventListener('click', () => {
    showView('sessionDetail');
});

// Stats View
async function loadStats() {
    const container = document.getElementById('pr-list');
    container.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const stats = await API.get('/api/stats/prs');

        if (stats.prs.length === 0) {
            container.innerHTML = '<div class="empty-state"><p>No PRs yet. Start lifting!</p></div>';
            return;
        }

        container.innerHTML = stats.prs.map(pr => {
            const date = new Date(pr.date);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            return `
                <div class="pr-item" data-exercise-id="${pr.exercise_id}">
                    <div>
                        <div class="pr-exercise">${pr.exercise_name}</div>
                        <div class="pr-details">${pr.reps} reps @ ${dateStr}</div>
                    </div>
                    <div class="pr-weight">${pr.weight} lbs</div>
                </div>
            `;
        }).join('');

        container.querySelectorAll('.pr-item').forEach(item => {
            item.style.cursor = 'pointer';
            item.addEventListener('click', () => loadExerciseHistory(parseInt(item.dataset.exerciseId)));
        });
    } catch (e) {
        console.error('Error loading stats:', e);
        container.innerHTML = '<div class="empty-state"><p>Failed to load stats</p></div>';
    }
}

// ============================================
// Image Gallery
// ============================================

function openGallery(exerciseName, images) {
    state.galleryImages = images;
    state.galleryIndex = 0;
    state.galleryExerciseName = exerciseName;

    document.getElementById('gallery-title').textContent = exerciseName;
    updateGalleryImage();
    updateGalleryDots();
    document.getElementById('image-gallery-modal').classList.remove('hidden');
}

function updateGalleryImage() {
    const img = state.galleryImages[state.galleryIndex];
    document.getElementById('gallery-image').src = img.url;
    document.getElementById('gallery-caption').textContent = img.caption || '';

    // Update nav buttons
    document.getElementById('gallery-prev').disabled = state.galleryIndex === 0;
    document.getElementById('gallery-next').disabled = state.galleryIndex === state.galleryImages.length - 1;
}

function updateGalleryDots() {
    const dotsContainer = document.getElementById('gallery-dots');
    dotsContainer.innerHTML = state.galleryImages.map((_, i) =>
        `<button class="gallery-dot ${i === state.galleryIndex ? 'active' : ''}" data-index="${i}"></button>`
    ).join('');

    dotsContainer.querySelectorAll('.gallery-dot').forEach(dot => {
        dot.addEventListener('click', () => {
            state.galleryIndex = parseInt(dot.dataset.index);
            updateGalleryImage();
            updateGalleryDots();
        });
    });
}

function closeGallery() {
    document.getElementById('image-gallery-modal').classList.add('hidden');
}

document.getElementById('gallery-close-btn').addEventListener('click', closeGallery);

document.getElementById('gallery-prev').addEventListener('click', () => {
    if (state.galleryIndex > 0) {
        state.galleryIndex--;
        updateGalleryImage();
        updateGalleryDots();
    }
});

document.getElementById('gallery-next').addEventListener('click', () => {
    if (state.galleryIndex < state.galleryImages.length - 1) {
        state.galleryIndex++;
        updateGalleryImage();
        updateGalleryDots();
    }
});

// Touch swipe support for gallery
let touchStartX = 0;
let touchEndX = 0;

document.getElementById('image-gallery-modal').addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, { passive: true });

document.getElementById('image-gallery-modal').addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, { passive: true });

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0 && state.galleryIndex < state.galleryImages.length - 1) {
            // Swipe left - next
            state.galleryIndex++;
            updateGalleryImage();
            updateGalleryDots();
        } else if (diff < 0 && state.galleryIndex > 0) {
            // Swipe right - prev
            state.galleryIndex--;
            updateGalleryImage();
            updateGalleryDots();
        }
    }
}

// Close gallery on backdrop click
document.getElementById('image-gallery-modal').addEventListener('click', (e) => {
    if (e.target.id === 'image-gallery-modal') {
        closeGallery();
    }
});

// Keyboard navigation for gallery
document.addEventListener('keydown', (e) => {
    if (document.getElementById('image-gallery-modal').classList.contains('hidden')) return;

    if (e.key === 'ArrowLeft' && state.galleryIndex > 0) {
        state.galleryIndex--;
        updateGalleryImage();
        updateGalleryDots();
    } else if (e.key === 'ArrowRight' && state.galleryIndex < state.galleryImages.length - 1) {
        state.galleryIndex++;
        updateGalleryImage();
        updateGalleryDots();
    } else if (e.key === 'Escape') {
        closeGallery();
    }
});

// ============================================
// Confirm Dialog
// ============================================

function showConfirmDialog(title, message, buttons) {
    document.getElementById('confirm-title').textContent = title;
    document.getElementById('confirm-message').textContent = message;

    const buttonsContainer = document.querySelector('.confirm-buttons');
    buttonsContainer.innerHTML = '';

    buttons.forEach(btn => {
        const button = document.createElement('button');
        button.className = `cds--btn ${btn.danger ? 'cds--btn--danger' : btn.primary ? 'cds--btn--primary' : 'cds--btn--secondary'}`;
        button.textContent = btn.label;
        button.addEventListener('click', () => {
            document.getElementById('confirm-modal').classList.add('hidden');
            if (btn.action) btn.action();
        });
        buttonsContainer.appendChild(button);
    });

    document.getElementById('confirm-modal').classList.remove('hidden');
}

// Close confirm on backdrop click
document.getElementById('confirm-modal').addEventListener('click', (e) => {
    if (e.target.id === 'confirm-modal') {
        document.getElementById('confirm-modal').classList.add('hidden');
    }
});

// Initialize
loadHome();
