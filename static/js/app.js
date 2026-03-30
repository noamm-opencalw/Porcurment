/* Porcurment — Main App JavaScript */

// ---- Suggestion chips ----
function fillSearch(text) {
    const input = document.getElementById('search-input');
    if (input) {
        input.value = text;
        input.focus();
    }
}

// ---- Loading overlay ----
const stages = ['search', 'analyze', 'rank'];
let currentStage = 0;
let stageInterval = null;

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('active');
        currentStage = 0;
        updateStages();
        stageInterval = setInterval(() => {
            currentStage++;
            if (currentStage >= stages.length) {
                currentStage = stages.length - 1;
            }
            updateStages();
        }, 8000);
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
    if (stageInterval) {
        clearInterval(stageInterval);
        stageInterval = null;
    }
}

function updateStages() {
    stages.forEach((stage, i) => {
        const el = document.getElementById(`stage-${stage}`);
        if (!el) return;
        el.classList.remove('active', 'done');
        if (i < currentStage) {
            el.classList.add('done');
            const icon = el.querySelector('.material-symbols-rounded');
            if (icon) icon.textContent = 'check_circle';
        } else if (i === currentStage) {
            el.classList.add('active');
            const icon = el.querySelector('.material-symbols-rounded');
            if (icon) icon.textContent = 'pending';
        }
    });
}

// ---- Form submission with loading ----
function handleSearchSubmit(event) {
    const input = document.getElementById('search-input');
    if (!input || !input.value.trim()) {
        event.preventDefault();
        input.focus();
        return false;
    }
    showLoading();
    return true;
}

// ---- Toast notifications ----
function showToast(message, duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 300ms ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ---- Export CSV ----
function exportCSV(searchId) {
    window.location.href = `/export/${searchId}`;
    showToast('Downloading CSV...');
}

// ---- Score bar animation ----
function animateScoreBars() {
    const bars = document.querySelectorAll('.score-bar-fill');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const width = bar.dataset.width;
                setTimeout(() => {
                    bar.style.width = width + '%';
                }, 100);
                observer.unobserve(bar);
            }
        });
    }, { threshold: 0.1 });

    bars.forEach(bar => {
        bar.style.width = '0%';
        observer.observe(bar);
    });
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    animateScoreBars();
});
