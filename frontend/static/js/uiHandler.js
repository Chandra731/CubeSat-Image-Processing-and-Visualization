import { logout } from './authHandler.js';
import { BASE_URL, displayImageHistory, displayClassificationHistory } from './apiHandler.js';


document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            const success = await logout();
            if (success) {
                // Redirect to login page or reload to update UI
                window.location.href = '/login';
            }
        });
    }

    // Add event listener for Image History button to open modal and load images
    const imageHistoryBtn = document.getElementById('image-history-btn');
    if (imageHistoryBtn) {
        imageHistoryBtn.addEventListener('click', async () => {
            const modal = document.getElementById('image-history-modal');
            const modalContent = document.getElementById('image-history-content');
            if (!modal || !modalContent) return;

            // Clear previous content
            modalContent.innerHTML = '';

            try {
                const response = await fetch(`${BASE_URL}/image_history`);
                const data = await response.json();

                if (!Array.isArray(data) || data.length === 0) {
                    modalContent.innerHTML = '<p>No image history available.</p>';
                } else {
                    // Use displayImageHistory from apiHandler.js to render images with metadata and controls
                    displayImageHistory(data, () => {
                        // Refresh image history on delete
                        imageHistoryBtn.click();
                    });
                }

                // Show modal (using Bootstrap's modal)
                $('#image-history-modal').modal('show');
            } catch (error) {
                modalContent.innerHTML = `<p>Error loading image history: ${error.message}</p>`;
                $('#image-history-modal').modal('show');
            }
        });
    }

    // Add event listener for Classification History button to open modal and load classifications
    const classificationHistoryBtn = document.getElementById('classification-history-btn');
    if (classificationHistoryBtn) {
        classificationHistoryBtn.addEventListener('click', async () => {
            const modal = document.getElementById('classification-history-modal');
            const modalContent = document.getElementById('classification-history-content');
            if (!modal || !modalContent) return;

            // Clear previous content
            modalContent.innerHTML = '';

            try {
                const response = await fetch(`${BASE_URL}/classification_history`);
                const data = await response.json();

                if (!Array.isArray(data) || data.length === 0) {
                    modalContent.innerHTML = '<p>No classification history available.</p>';
                } else {
                    // Use displayClassificationHistory from apiHandler.js to render classifications with metadata and controls
                    displayClassificationHistory(data, () => {
                        // Refresh classification history on delete
                        classificationHistoryBtn.click();
                    });
                }

                // Show modal (using Bootstrap's modal)
                $('#classification-history-modal').modal('show');
            } catch (error) {
                modalContent.innerHTML = `<p>Error loading classification history: ${error.message}</p>`;
                $('#classification-history-modal').modal('show');
            }
        });
    }

    // Add event listeners for filter inputs to refresh image list on input
    const filterLatInput = document.getElementById('filter-latitude');
    const filterLonInput = document.getElementById('filter-longitude');

    if (filterLatInput) {
        filterLatInput.addEventListener('input', () => {
            imageHistoryBtn.click();
        });
    }
    if (filterLonInput) {
        filterLonInput.addEventListener('input', () => {
            imageHistoryBtn.click();
        });
    }
});
