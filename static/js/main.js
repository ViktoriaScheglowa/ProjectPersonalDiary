class DiaryUtils {
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    static confirmAction(message) {
        return confirm(message);
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Delete confirmation handler
document.addEventListener('DOMContentLoaded', function() {
    // Delete confirmation
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!DiaryUtils.confirmAction('Вы уверены, что хотите удалить эту запись?')) {
                e.preventDefault();
            }
        });
    });

    // Favorite toggle
    const favoriteButtons = document.querySelectorAll('.btn-favorite');
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const entryId = this.getAttribute('data-entry-id');
            this.classList.toggle('active');

            // Send AJAX request to toggle favorite
            fetch(`/entries/${entryId}/toggle_favorite/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    DiaryUtils.showNotification('Избранное обновлено');
                }
            });
        });
    });

    // Image preview for forms
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('.image-preview') ||
                                   document.createElement('div');
                    preview.className = 'image-preview';
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    input.parentNode.appendChild(preview);
                };
                reader.readAsDataURL(file);
            }
        });
    });
});

// CSRF token helper for AJAX requests
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}