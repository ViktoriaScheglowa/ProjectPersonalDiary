class EntryFilters {
    constructor() {
        this.filters = {
            all: 'all',
            today: 'today',
            week: 'week',
            month: 'month',
            favorites: 'favorites'
        };

        this.currentFilter = this.filters.all;
        this.entries = [];

        this.init();
    }

    init() {
        this.bindEvents();
        this.loadEntries();
    }

    bindEvents() {
        // Filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const filter = e.target.getAttribute('data-filter');
                this.applyFilter(filter);
            });
        });

        // Search input
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchEntries(e.target.value);
            });
        }

        // Tag filters
        const tagFilters = document.querySelectorAll('.tag-filter');
        tagFilters.forEach(tag => {
            tag.addEventListener('click', (e) => {
                const tagName = e.target.getAttribute('data-tag');
                this.filterByTag(tagName);
            });
        });

        // Sort select
        const sortSelect = document.querySelector('.sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortEntries(e.target.value);
            });
        }
    }

    loadEntries() {
        // Get entries from the page or load via AJAX
        const entryElements = document.querySelectorAll('.entry-card');
        this.entries = Array.from(entryElements).map(entry => ({
            element: entry,
            date: new Date(entry.getAttribute('data-date')),
            tags: entry.getAttribute('data-tags') ?
                  entry.getAttribute('data-tags').split(',') : [],
            title: entry.querySelector('.entry-title').textContent,
            content: entry.querySelector('.entry-content').textContent,
            isFavorite: entry.classList.contains('favorite')
        }));
    }

    applyFilter(filterType) {
        this.currentFilter = filterType;

        // Update active button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filterType}"]`).classList.add('active');

        // Apply filter
        this.entries.forEach(entry => {
            let shouldShow = true;

            switch (filterType) {
                case this.filters.today:
                    shouldShow = this.isToday(entry.date);
                    break;
                case this.filters.week:
                    shouldShow = this.isThisWeek(entry.date);
                    break;
                case this.filters.month:
                    shouldShow = this.isThisMonth(entry.date);
                    break;
                case this.filters.favorites:
                    shouldShow = entry.isFavorite;
                    break;
                case this.filters.all:
                default:
                    shouldShow = true;
            }

            this.toggleEntryVisibility(entry.element, shouldShow);
        });

        this.updateEntryCount();
    }

    filterByTag(tagName) {
        this.entries.forEach(entry => {
            const hasTag = entry.tags.includes(tagName);
            this.toggleEntryVisibility(entry.element, hasTag);
        });

        this.updateEntryCount();
    }

    searchEntries(query) {
        const searchTerm = query.toLowerCase().trim();

        this.entries.forEach(entry => {
            const matches = entry.title.toLowerCase().includes(searchTerm) ||
                           entry.content.toLowerCase().includes(searchTerm);
            this.toggleEntryVisibility(entry.element, matches);
        });

        this.updateEntryCount();
    }

    sortEntries(sortBy) {
        const entriesContainer = document.querySelector('.entries-grid');
        const entryElements = Array.from(this.entries);

        switch (sortBy) {
            case 'date-desc':
                entryElements.sort((a, b) => b.date - a.date);
                break;
            case 'date-asc':
                entryElements.sort((a, b) => a.date - b.date);
                break;
            case 'title':
                entryElements.sort((a, b) => a.title.localeCompare(b.title));
                break;
        }

        // Reorder elements in DOM
        entryElements.forEach(entry => {
            entriesContainer.appendChild(entry.element);
        });
    }

    toggleEntryVisibility(element, show) {
        if (show) {
            element.style.display = 'block';
            element.classList.remove('hidden');
        } else {
            element.style.display = 'none';
            element.classList.add('hidden');
        }
    }

    isToday(date) {
        const today = new Date();
        return date.toDateString() === today.toDateString();
    }

    isThisWeek(date) {
        const today = new Date();
        const startOfWeek = new Date(today.setDate(today.getDate() - today.getDay()));
        const endOfWeek = new Date(today.setDate(today.getDate() + 6));
        return date >= startOfWeek && date <= endOfWeek;
    }

    isThisMonth(date) {
        const today = new Date();
        return date.getMonth() === today.getMonth() &&
               date.getFullYear() === today.getFullYear();
    }

    updateEntryCount() {
        const visibleCount = this.entries.filter(entry =>
            entry.element.style.display !== 'none'
        ).length;

        const countElement = document.querySelector('.entries-count');
        if (countElement) {
            countElement.textContent = `Найдено записей: ${visibleCount}`;
        }
    }
}

// Initialize filters when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.entries-section')) {
        new EntryFilters();
    }
});