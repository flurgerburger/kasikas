document.addEventListener('DOMContentLoaded', function () {
    const track = document.getElementById('reel-carousel-track');
    const prevBtn = document.getElementById('reel-prev-btn');
    const nextBtn = document.getElementById('reel-next-btn');
    const shell = document.querySelector('.reel-carousel-shell');

    if (!track || !prevBtn || !nextBtn) {
        return;
    }

    function getStepSize() {
        const firstCard = track.querySelector('.reel-card');
        if (!firstCard) {
            return 340;
        }
        const style = window.getComputedStyle(track);
        const gap = parseFloat(style.columnGap || style.gap || '18') || 18;
        return firstCard.getBoundingClientRect().width + gap;
    }

    function updateButtons() {
        const maxScroll = track.scrollWidth - track.clientWidth;
        const atStart = track.scrollLeft <= 2;
        const atEnd = maxScroll <= 2 || track.scrollLeft >= maxScroll - 2;

        prevBtn.disabled = atStart;
        prevBtn.setAttribute('aria-disabled', atStart ? 'true' : 'false');
        nextBtn.disabled = atEnd;
        nextBtn.setAttribute('aria-disabled', atEnd ? 'true' : 'false');
    }

    function scrollByStep(direction) {
        const step = getStepSize();
        track.scrollBy({
            left: direction * step,
            behavior: 'smooth',
        });
    }

    prevBtn.addEventListener('click', function () {
        scrollByStep(-1);
    });

    nextBtn.addEventListener('click', function () {
        scrollByStep(1);
    });

    if (shell) {
        shell.addEventListener('keydown', function (event) {
            if (event.key === 'ArrowLeft') {
                event.preventDefault();
                scrollByStep(-1);
            } else if (event.key === 'ArrowRight') {
                event.preventDefault();
                scrollByStep(1);
            }
        });
    }

    track.addEventListener('scroll', updateButtons, { passive: true });
    window.addEventListener('resize', updateButtons);
    updateButtons();
});
