import {} from './uiHandler.js'; // Removed import of displayImageHistory as it does not exist

export const BASE_URL = 'http://127.0.0.1:5001/api';

/**
 * Wrapper for fetch API calls with consistent error handling and JSON parsing.
 * @param {string} url - The URL to fetch.
 * @param {object} options - Fetch options.
 * @returns {Promise<any>} - Parsed JSON response.
 * @throws Will throw an error if fetch fails or response is not ok.
 */
export async function fetchWrapper(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Fetch error for ${url}:`, error);
        throw error;
    }
}

/**
 * Fetch CubeSat positional data and update the Cesium viewer.
 */
export async function fetchCubeSatData(viewer) {
    try {
        const data = await fetchWrapper(`${BASE_URL}/cubesat_positions`);

        console.log("Received API Data:", data); // Log raw API response

        if (!Array.isArray(data)) {
            throw new Error('Invalid data format: Expected an array');
        }

        data.forEach(sat => {
            console.log("📡 Processing satellite:", sat); // Log each satellite entry

            if (sat.lat === undefined || sat.lon === undefined || sat.alt === undefined) {
                console.error('Missing required fields:', sat);
                return;
            }

            if (isNaN(sat.lat) || isNaN(sat.lon) || isNaN(sat.alt)) {
                console.error('Invalid number values:', sat);
                return;
            }

            const position = Cesium.Cartesian3.fromDegrees(sat.lon, sat.lat, sat.alt * 1000);
            viewer.entities.add({
                position: position,
                point: { pixelSize: 8, color: Cesium.Color.RED },
                label: {
                    text: sat.satellite,
                    font: '14px sans-serif',
                    fillColor: Cesium.Color.WHITE,
                    showBackground: true
                },
                path: {
                    show: true,
                    leadTime: 0,
                    trailTime: 60 * 60 * 24, // 24 hours trail
                    width: 2,
                    resolution: 120,
                    material: new Cesium.PolylineGlowMaterialProperty({
                        glowPower: 0.16,
                        color: Cesium.Color.BLUE
                    })
                }
            });
        });
    } catch (error) {
        console.error('Error fetching CubeSat data:', error);
    }
}

/**
 * Capture an image using CubeSat coordinates from Google Earth Engine.
 */
export async function captureImage(latitude, longitude, dataset) {
    // Validate coordinates before sending
    if (typeof latitude !== 'number' || typeof longitude !== 'number' ||
        latitude < -90 || latitude > 90 || 
        longitude < -180 || longitude > 180) {
        throw new Error('Invalid coordinates: Latitude must be between -90 and 90, Longitude between -180 and 180');
    }

    try {
        const data = await fetchWrapper(`${BASE_URL}/capture_image`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                latitude: Number(latitude), 
                longitude: Number(longitude),
                dataset: dataset
            }),
        });

        console.log("Capture Response:", data);

        if (data.error) {
            throw new Error(data.error);
        }

        // Removed call to storeImageInDatabase to avoid duplicate records
        if (data.rgb_url) {
            // Update the displayed images src to the URLs
            const rgbImage = document.getElementById("rgb-image");
            if (rgbImage) {
               
                rgbImage.src = data.raw_rgb_url;
            }
            const ndviImage = document.getElementById("ndvi-image");
            if (ndviImage) {
                ndviImage.src = data.ndvi_url;
            }
            const eviImage = document.getElementById("evi-image");
            if (eviImage) {
                eviImage.src = data.evi_url;
            }
            const saviImage = document.getElementById("savi-image");
            if (saviImage) {
                saviImage.src = data.savi_url;
            }
            const gciImage = document.getElementById("gci-image");
            if (gciImage) {
                gciImage.src = data.gci_url;
            }
        }
        console.log("Returning capture data:", data);
        return data;
    } catch (error) {
        console.error('Error capturing image:', error);
        throw error;
    }
}

/**
 * Fetch and display stored image history.
 */
export async function fetchImageHistory() {
    try {
        const data = await fetchWrapper(`${BASE_URL}/image_history`);

        console.log("Image History Data:", data);

        if (!Array.isArray(data)) {
            throw new Error("Invalid image history format. Expected an array.");
        }

        if (data.length === 0) {
            console.warn("No images found in history.");
        }

        displayImageHistory(data, fetchImageHistory);
    } catch (error) {
        console.error('Error fetching image history:', error);
    }
}

/**
 * Render image history data into the UI.
 * @param {Array} images - Array of image objects.
 * @param {Function} refreshCallback - Function to refresh the image history list.
 */
export function displayImageHistory(images, refreshCallback) {
    const container = document.getElementById('image-history-content');
    if (!container) {
        console.error('Image history container not found');
        return;
    }

    container.innerHTML = '';

    // Get filter values
    const filterLatInput = document.getElementById('filter-latitude');
    const filterLonInput = document.getElementById('filter-longitude');
    const filterLat = filterLatInput ? filterLatInput.value.trim() : '';
    const filterLon = filterLonInput ? filterLonInput.value.trim() : '';

    // Filter images based on latitude and longitude if filters are set
    const filteredImages = images.filter(image => {
        let latMatch = true;
        let lonMatch = true;

        if (filterLat !== '') {
            latMatch = image.latitude !== null && image.latitude.toString().includes(filterLat);
        }
        if (filterLon !== '') {
            lonMatch = image.longitude !== null && image.longitude.toString().includes(filterLon);
        }
        return latMatch && lonMatch;
    });

    if (filteredImages.length === 0) {
        container.innerHTML = '<p>No images match the filter criteria.</p>';
        return;
    }

    filteredImages.forEach(image => {
        const card = document.createElement('div');
        card.className = 'card m-2';
        card.style.width = '220px';

        const img = document.createElement('img');
        // Use raw_rgb_url if available, else fallback to image_url
        const imgSrc = image.raw_rgb_url ? image.raw_rgb_url : image.image_url;
        img.src = imgSrc.startsWith('http') ? imgSrc : `${window.location.origin}/static/${imgSrc}`;
        img.className = 'card-img-top';
        img.alt = 'Image History';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body p-2';

        const latText = document.createElement('p');
        latText.className = 'card-text mb-1';
        latText.textContent = `Latitude: ${image.latitude !== null ? image.latitude : 'N/A'}`;

        const lonText = document.createElement('p');
        lonText.className = 'card-text mb-1';
        lonText.textContent = `Longitude: ${image.longitude !== null ? image.longitude : 'N/A'}`;

        const btnGroup = document.createElement('div');
        btnGroup.className = 'btn-group btn-group-sm';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-danger';
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete this image?')) {
                try {
                    const response = await fetch(`${BASE_URL}/delete_image/${image.id}`, {
                        method: 'DELETE',
                    });
                    const result = await response.json();
                    if (response.ok) {
                        alert('Image deleted successfully');
                        if (typeof refreshCallback === 'function') {
                            refreshCallback();
                        }
                    } else {
                        alert('Failed to delete image: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Error deleting image: ' + error.message);
                }
            }
        });

        const downloadBtn = document.createElement('a');
        downloadBtn.className = 'btn btn-primary';
        downloadBtn.textContent = 'Download';
        downloadBtn.href = image.image_url.startsWith('http') ? image.image_url : `${window.location.origin}/static/${image.image_url}`;
        downloadBtn.download = '';
        downloadBtn.target = '_blank';
        downloadBtn.rel = 'noopener noreferrer';

        btnGroup.appendChild(deleteBtn);
        btnGroup.appendChild(downloadBtn);

        cardBody.appendChild(latText);
        cardBody.appendChild(lonText);
        cardBody.appendChild(btnGroup);

        card.appendChild(img);
        card.appendChild(cardBody);

        container.appendChild(card);
    });
}

/**
 * Fetch and display classification history.
 */
export async function fetchClassificationHistory() {
    try {
        const data = await fetchWrapper(`${BASE_URL}/classification_history`);

        console.log("Classification History Data:", data);

        if (!Array.isArray(data)) {
            throw new Error("Invalid classification history format. Expected an array.");
        }

        if (data.length === 0) {
            console.warn("No classifications found in history.");
        }

        displayClassificationHistory(data, fetchClassificationHistory);
    } catch (error) {
        console.error('Error fetching classification history:', error);
    }
}

/**
 * Render classification history data into the UI.
 * @param {Array} classifications - Array of classification objects.
 * @param {Function} refreshCallback - Function to refresh the classification history list.
 */
export function displayClassificationHistory(classifications, refreshCallback) {
    const container = document.getElementById('classification-history-content');
    if (!container) {
        console.error('Classification history container not found');
        return;
    }

    container.innerHTML = '';

    classifications.forEach(classification => {
        const card = document.createElement('div');
        card.className = 'card m-2';
        card.style.width = '220px';

        const img = document.createElement('img');
        img.src = classification.image_url.startsWith('http') ? classification.image_url : `${window.location.origin}/static/${classification.image_url}`;
        img.className = 'card-img-top';
        img.alt = 'Classification Image';

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body p-2';

        const classText = document.createElement('p');
        classText.className = 'card-text mb-1';
        classText.textContent = `Classification: ${classification.classification}`;

        const confidenceText = document.createElement('p');
        confidenceText.className = 'card-text mb-1';
        confidenceText.textContent = `Confidence: ${classification.confidence}`;

        const btnGroup = document.createElement('div');
        btnGroup.className = 'btn-group btn-group-sm';

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-danger';
        deleteBtn.textContent = 'Delete';
        deleteBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to delete this classification?')) {
                try {
                    const response = await fetch(`${BASE_URL}/delete_image/${classification.id}`, {
                        method: 'DELETE',
                    });
                    const result = await response.json();
                    if (response.ok) {
                        alert('Classification deleted successfully');
                        if (typeof refreshCallback === 'function') {
                            refreshCallback();
                        }
                    } else {
                        alert('Failed to delete classification: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Error deleting classification: ' + error.message);
                }
            }
        });

        btnGroup.appendChild(deleteBtn);

        cardBody.appendChild(classText);
        cardBody.appendChild(confidenceText);
        cardBody.appendChild(btnGroup);

        card.appendChild(img);
        card.appendChild(cardBody);

        container.appendChild(card);
    });
}

/**
 * Store the captured image URLs in the database.
 */
export async function storeImageInDatabase(imageData) {
    try {
        const response = await fetch(`${BASE_URL}/store_image`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(imageData),
        });

        const result = await response.json();
        console.log("Image stored successfully:", result);
        return result;
    } catch (error) {
        console.error('Error storing image in database:', error);
        throw error;
    }
}

