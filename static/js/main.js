/* ── Modal handling ───────────────────────────────── */
const modal = document.getElementById('detail-modal');
const closeBtn = modal?.querySelector('button[aria-label="Close"]');

function closeModal() {
    modal?.classList.remove('modal-visible');
    document.body.style.overflow = '';
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
        if (window.innerWidth >= 768) {
            closeMenu();
        }
    });
})();

/* ── Card interactions ─────────────────────────────────── */
document.querySelectorAll('.card-scene').forEach(scene => {
    /* apply staggered animation delay from data attribute */
    const delay = scene.dataset.delay;
    if (delay) scene.style.animationDelay = delay + 'ms';

    const card = scene.querySelector('.movie-card');
    if (!card) return;

    /* ── Click to open modal ───────────────────────────────── */
    scene.addEventListener('click', (e) => {
        if (!modal) return;

        // Populate modal with data
        const titleEl = document.getElementById('modal-title');
        const ratingEl = document.getElementById('modal-rating');
        const dateEl = document.getElementById('modal-date');
        const overviewEl = document.getElementById('modal-overview');
        const posterImg = document.getElementById('modal-poster');

        if (titleEl) titleEl.textContent = scene.dataset.title || 'N/A';
        if (ratingEl) ratingEl.textContent = scene.dataset.rating || '—';
        if (dateEl) dateEl.textContent = scene.dataset.date || 'Unknown';
        if (overviewEl) overviewEl.textContent = scene.dataset.overview || 'No description available.';

        // Handle seasons/episodes for series pages specifically
        const seasonsElement = document.getElementById('modal-seasons');
        if (seasonsElement) {
            const seasons = scene.dataset.seasons;
            const episodes = scene.dataset.episodes;
            if (seasons && episodes && (parseInt(seasons) > 0 || parseInt(episodes) > 0)) {
                seasonsElement.textContent = `${seasons} Seasons • ${episodes} Episodes`;
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

    /* ── Mouse interactions for 3D tilt ─────────────────────────────── */
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
