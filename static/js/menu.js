document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const mainNav = document.querySelector('.main-nav');
    const header = document.querySelector('.header-hover-menu');

    // Create overlay for mobile
    const overlay = document.createElement('div');
    overlay.className = 'menu-overlay';
    document.body.appendChild(overlay);

    // Mobile menu functionality
    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            mainNav.classList.toggle('active');
            overlay.classList.toggle('active');
        });

        overlay.addEventListener('click', function() {
            mainNav.classList.remove('active');
            overlay.classList.remove('active');
        });

        // Mobile dropdown functionality
        const dropdownToggles = mainNav.querySelectorAll('.dropdown-toggle');
        dropdownToggles.forEach(function(toggle) {
            toggle.addEventListener('click', function(e) {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    const dropdown = this.parentElement;
                    dropdown.classList.toggle('active');
                }
            });
        });

        // Close menu on link click (mobile)
        const menuLinks = mainNav.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    mainNav.classList.remove('active');
                    overlay.classList.remove('active');

                    // Close all dropdowns
                    dropdownToggles.forEach(toggle => {
                        toggle.parentElement.classList.remove('active');
                    });
                }
            });
        });
    }

    // Close menu when clicking outside (desktop)
    document.addEventListener('click', function(e) {
        if (window.innerWidth > 768 && header && !header.contains(e.target)) {
            // Menu will auto-close due to CSS :hover
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            // Reset mobile menu state
            if (mainNav) mainNav.classList.remove('active');
            overlay.classList.remove('active');

            // Close all mobile dropdowns
            const dropdowns = document.querySelectorAll('.dropdown');
            dropdowns.forEach(function(dropdown) {
                dropdown.classList.remove('active');
            });
        }
    });
});