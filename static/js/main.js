/* ── Shared state ─────────────────────────────────────── */
let currentMediaId = null;
let currentMediaType = 'movie';

/* ── Modal handling ───────────────────────────────── */
const modal = document.getElementById('detail-modal');
const closeBtn = modal?.querySelector('button[aria-label="Close"]');

function resetTrailer() {
    const btn = document.getElementById('trailer-btn');
    const embed = document.getElementById('trailer-embed');
    if (btn) {
        btn.disabled = false;
        btn.dataset.state = 'idle';
        btn.className = 'trailer-btn';
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
            </svg>
            Watch Trailer`;
    }
    if (embed) {
        embed.innerHTML = '';
        embed.classList.add('hidden');
    }
}

function closeModal() {
    modal?.classList.remove('modal-visible');
    document.body.style.overflow = '';
    resetTrailer();
}

function openModal() {
    modal?.classList.add('modal-visible');
    document.body.style.overflow = 'hidden';
}

closeBtn?.addEventListener('click', closeModal);
modal?.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
});
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal?.classList.contains('modal-visible')) closeModal();
});

/* ── Trailer button ───────────────────────────────────── */
document.getElementById('trailer-btn')?.addEventListener('click', async function () {
    const btn = this;
    const embed = document.getElementById('trailer-embed');
    if (!embed || !currentMediaId) return;

    if (btn.dataset.state === 'playing') {
        embed.innerHTML = '';
        embed.classList.add('hidden');
        btn.dataset.state = 'idle';
        btn.className = 'trailer-btn';
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
            </svg>
            Watch Trailer`;
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="trailer-spinner"></span> Loading\u2026';

    try {
        const res = await fetch(`/trailer/${currentMediaType}/${currentMediaId}`);
        const data = await res.json();

        if (data.key) {
            embed.innerHTML = `<iframe
                src="https://www.youtube.com/embed/${data.key}?autoplay=1&rel=0"
                allow="autoplay; encrypted-media; fullscreen"
                allowfullscreen></iframe>`;
            embed.classList.remove('hidden');
            btn.disabled = false;
            btn.dataset.state = 'playing';
            btn.className = 'trailer-btn playing';
            btn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
                Hide Trailer`;
        } else {
            btn.innerHTML = 'No trailer available';
            btn.disabled = true;
        }
    } catch {
        btn.disabled = false;
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
            </svg>
            Try Again`;
    }
});

/* ── Mobile nav (hamburger) ───────────────────────────── */
(function () {
    const toggle = document.getElementById('mobile-menu-toggle');
    const menu = document.getElementById('mobile-menu');
    if (!toggle || !menu) return;

    const closeMenu = () => {
        menu.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
    };

    toggle.addEventListener('click', (event) => {
        event.stopPropagation();
        const isOpen = menu.classList.toggle('open');
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    document.addEventListener('click', (event) => {
        if (!menu.classList.contains('open')) return;
        if (menu.contains(event.target) || toggle.contains(event.target)) return;
        closeMenu();
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth >= 768) closeMenu();
    });
})();

/* ── Card interactions ─────────────────────────────────── */
document.querySelectorAll('.card-scene').forEach(scene => {
    const delay = scene.dataset.delay;
    if (delay) scene.style.animationDelay = delay + 'ms';

    const card = scene.querySelector('.movie-card');
    if (!card) return;

    scene.addEventListener('click', () => {
        if (!modal) return;

        currentMediaId = scene.dataset.id || null;
        currentMediaType = scene.dataset.mediaType || 'movie';

        resetTrailer();

        const titleEl = document.getElementById('modal-title');
        const ratingEl = document.getElementById('modal-rating');
        const dateEl = document.getElementById('modal-date');
        const overviewEl = document.getElementById('modal-overview');
        const posterImg = document.getElementById('modal-poster');

        if (titleEl) titleEl.textContent = scene.dataset.title || 'N/A';
        if (ratingEl) ratingEl.textContent = scene.dataset.rating || '\u2014';
        if (dateEl) dateEl.textContent = scene.dataset.date || 'Unknown';
        if (overviewEl) overviewEl.textContent = scene.dataset.overview || 'No description available.';

        const seasonsElement = document.getElementById('modal-seasons');
        if (seasonsElement) {
            const seasons = scene.dataset.seasons;
            const episodes = scene.dataset.episodes;
            if (seasons && episodes && (parseInt(seasons) > 0 || parseInt(episodes) > 0)) {
                seasonsElement.textContent = `${seasons} Seasons \u2022 ${episodes} Episodes`;
                seasonsElement.classList.remove('hidden');
            } else {
                seasonsElement.classList.add('hidden');
            }
        }

        const poster = scene.dataset.poster;
        if (posterImg) {
            posterImg.alt = scene.dataset.title || 'Poster';
            posterImg.src = poster
                ? `https://image.tmdb.org/t/p/w500${poster}`
                : "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='600'%3E%3Crect fill='%2311151E' width='400' height='600'/%3E%3C/svg%3E";
        }

        openModal();
    });

    scene.addEventListener('mousemove', e => {
        const r = scene.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = `translateY(-10px) rotateX(${(-y * 10).toFixed(2)}deg) rotateY(${(x * 10).toFixed(2)}deg) scale(1.03)`;
    });

    scene.addEventListener('mouseleave', () => {
        card.style.transform = '';
    });
});