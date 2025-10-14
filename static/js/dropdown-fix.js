document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');

    // Сначала скрываем все выпадающие меню
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.style.display = 'none';
    });

    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (toggle && menu) {
            // Показываем меню при наведении
            dropdown.addEventListener('mouseenter', function() {
                menu.style.display = 'block';
                menu.style.opacity = '1';
                menu.style.visibility = 'visible';
            });

            // Скрываем меню при уходе курсора
            dropdown.addEventListener('mouseleave', function() {
                menu.style.display = 'none';
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
            });
        }
    });
});