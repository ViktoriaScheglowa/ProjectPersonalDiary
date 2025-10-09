
class DiaryCarousel {
    constructor(container) {
        this.container = container;
        this.slides = container.querySelector('.carousel-slides');
        this.slideItems = container.querySelectorAll('.carousel-slide');
        this.prevBtn = container.querySelector('.carousel-btn.prev');
        this.nextBtn = container.querySelector('.carousel-btn.next');
        this.indicators = container.querySelectorAll('.indicator');
        this.currentSlide = 0;
        this.slideInterval = null;
        this.autoSlideDelay = 5000;

        this.init();
    }

    init() {
        // Event listeners
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.next());
        }

        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prev());
        }

        // Indicators
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.goToSlide(index));
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.prev();
            if (e.key === 'ArrowRight') this.next();
        });

        // Auto slide
        this.startAutoSlide();

        // Pause on hover
        this.container.addEventListener('mouseenter', () => this.stopAutoSlide());
        this.container.addEventListener('mouseleave', () => this.startAutoSlide());

        // Touch events for mobile
        this.addTouchEvents();
    }

    showSlide(index) {
        this.currentSlide = (index + this.slideItems.length) % this.slideItems.length;
        this.slides.style.transform = `translateX(-${this.currentSlide * 100}%)`;

        // Update indicators
        this.updateIndicators();

        // Dispatch custom event
        this.container.dispatchEvent(new CustomEvent('slideChange', {
            detail: { currentSlide: this.currentSlide }
        }));
    }

    updateIndicators() {
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide);
        });
    }

    next() {
        this.showSlide(this.currentSlide + 1);
        this.restartAutoSlide();
    }

    prev() {
        this.showSlide(this.currentSlide - 1);
        this.restartAutoSlide();
    }

    goToSlide(index) {
        this.showSlide(index);
        this.restartAutoSlide();
    }

    startAutoSlide() {
        if (this.slideItems.length > 1) {
            this.slideInterval = setInterval(() => this.next(), this.autoSlideDelay);
        }
    }

    stopAutoSlide() {
        if (this.slideInterval) {
            clearInterval(this.slideInterval);
            this.slideInterval = null;
        }
    }

    restartAutoSlide() {
        this.stopAutoSlide();
        this.startAutoSlide();
    }

    addTouchEvents() {
        let startX = 0;
        let endX = 0;

        this.container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });

        this.container.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            this.handleSwipe(startX, endX);
        });
    }

    handleSwipe(startX, endX) {
        const swipeThreshold = 50;
        const diff = startX - endX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                this.next(); // Swipe left
            } else {
                this.prev(); // Swipe right
            }
        }
    }

    destroy() {
        this.stopAutoSlide();
        // Remove event listeners if needed
    }
}

// Initialize all carousels on the page
document.addEventListener('DOMContentLoaded', function() {
    const carousels = document.querySelectorAll('.carousel');

    carousels.forEach(container => {
        new DiaryCarousel(container);
    });
});