import { initializeCesium } from "./cesiumSetup.js";
import { fetchCubeSatData, captureImage, fetchImageHistory } from "./apiHandler.js";
// Removed import of setupUIInteractions as it does not exist in uiHandler.js
import { initializeHeatmap } from "./heatmap.js";
import { initializeCharts } from "./charts.js";

import { BASE_URL } from './apiHandler.js';

document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Check login status and update navbar
        const statusResponse = await fetch(`${BASE_URL.replace('/api', '')}/auth/status`, {
            credentials: 'include',
        });
        const statusData = await statusResponse.json();
        const navbarNav = document.querySelector('.navbar-nav.ms-auto');
        if (navbarNav) {
            if (statusData.success) {
                // User is logged in, update navbar
                const userItem = document.createElement('li');
                userItem.className = 'nav-item dropdown';
                userItem.innerHTML = `
                    <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="bi bi-person-circle"></i> ${statusData.user.username}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                        <li><a class="dropdown-item" href="/visualization">Visualization</a></li>
                        <li><a class="dropdown-item" href="#" id="logoutBtn">Logout</a></li>
                    </ul>
                `;
                // Remove existing login button by href
                const loginBtnLi = Array.from(navbarNav.querySelectorAll('li.nav-item')).find(li => {
                    const a = li.querySelector('a.nav-link, a.btn');
                    return a && a.getAttribute('href') === '/login';
                });
                if (loginBtnLi) {
                    loginBtnLi.remove();
                }
                navbarNav.appendChild(userItem);
                // Logout handler
                document.getElementById('logoutBtn').addEventListener('click', async (e) => {
                    e.preventDefault();
                    try {
                        const logoutResponse = await fetch(`${BASE_URL.replace('/api', '')}/auth/logout`, {
                            method: 'POST',
                            credentials: 'include',
                        });
                        const logoutData = await logoutResponse.json();
                        if (logoutData.success) {
                            window.location.href = '/';
                        } else {
                            alert('Logout failed');
                        }
                    } catch (err) {
                        alert('Logout failed');
                    }
                });
            } else {
                // User not logged in, ensure login button is present
                // (Assuming index.html already has login button)
            }
        }
        // Remove redirect to login to allow access to visualization without login
        // if (!statusData.success && window.location.pathname === '/visualization') {
        //     window.location.href = '/auth';
        // }

        // Upload button event handler
        const uploadBtn = document.getElementById("upload-btn");
        const uploadInput = document.getElementById("userImageUpload");
        const uploadStatusText = document.getElementById("upload-status-text");
        const uploadStatusProgress = document.getElementById("upload-status-progress");

        if (uploadBtn && uploadInput) {
            uploadBtn.addEventListener("click", async () => {
                if (uploadInput.files.length === 0) {
                    alert("Please select a file to upload.");
                    return;
                }
                const file = uploadInput.files[0];
                const formData = new FormData();
                formData.append("image_file", file);

                try {
                    uploadStatusText.textContent = "Uploading...";
                    uploadStatusProgress.style.width = "0%";

                    const response = await fetch(`${BASE_URL}/upload_image`, {
                        method: "POST",
                        body: formData,
                    });

                    const data = await response.json();

                    if (data.error) {
                        uploadStatusText.textContent = "Upload failed.";
                        alert("Upload failed: " + data.error);
                        return;
                    }

                    uploadStatusText.textContent = "Upload successful.";
                    uploadStatusProgress.style.width = "100%";

                    // Store uploaded image URL for classification
                    if (data.image_url) {
                        window.localStorage.setItem("local_rgb_url", data.image_url);
                        const rgbImage = document.getElementById("rgb-image");
                        if (rgbImage) {
                            rgbImage.src = `${BASE_URL.replace('/api', '')}/static/${data.image_url}`;
                        }
                    }

                    // Trigger classification after upload
                    if (data.image_url) {
                        try {
                            const classifyResponse = await fetch(`${BASE_URL}/classify_image`, {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ image_url: data.image_url }),
                            });

                            const classifyData = await classifyResponse.json();

                            if (classifyData.error) {
                                alert("Classification failed: " + classifyData.error);
                                return;
                            }

                            const classificationResults = classifyData.classification_percentages;
                            const classificationList = document.getElementById("classification-list");
                            classificationList.innerHTML = "";

                            for (const [className, percentage] of Object.entries(classificationResults)) {
                                const li = document.createElement("li");
                                li.className = "list-group-item";
                                li.textContent = `${className}: ${percentage}%`;
                                classificationList.appendChild(li);
                            }

                            document.getElementById("classification-results").style.display = "block";
                        } catch (error) {
                            alert("Error during classification: " + error.message);
                        }
                    }
                } catch (error) {
                    uploadStatusText.textContent = "Upload failed.";
                    alert("Upload failed: " + error.message);
                }
            });
        }

        // Initialize Cesium viewer and UI interactions
        const viewer = initializeCesium();
        // Removed call to setupUIInteractions as it does not exist
        await fetchCubeSatData(viewer);

        // Fetch CubeSat orbits data
        const response = await fetch("http://127.0.0.1:5001/api/cubesat_orbits");
        const data = await response.json();

        if (!Array.isArray(data)) throw new TypeError("Expected an array of CubeSat data");

        data.forEach(satellite => {
            if (!satellite.orbit || satellite.orbit.length === 0) return;

            const orbitPath = new Cesium.SampledPositionProperty();
            satellite.orbit.forEach((point, index) => {
                if (!point.timestamp || isNaN(new Date(point.timestamp).getTime())) return;
                const position = Cesium.Cartesian3.fromDegrees(point.lon, point.lat, point.alt * 1000);
                const time = Cesium.JulianDate.fromDate(new Date(point.timestamp));
                orbitPath.addSample(time, position);
            });

            if (orbitPath._property._times.length === 0) return;

            const satelliteEntity = viewer.entities.add({
                name: satellite.satellite,
                position: orbitPath,
                point: { pixelSize: 8, color: Cesium.Color.RED },
                label: {
                    text: satellite.satellite,
                    font: "14px sans-serif",
                    fillColor: Cesium.Color.WHITE,
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 2,
                    style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                    pixelOffset: new Cesium.Cartesian2(0, -20),
                    verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                    show: false, // Hide labels initially
                },
                path: {
                    material: new Cesium.PolylineGlowMaterialProperty({ glowPower: 0.1, color: Cesium.Color.YELLOW }),
                    width: 3,
                    leadTime: 90,
                    trailTime: 90,
                },
            });

            satelliteEntity.description = `
                <h3>${satellite.satellite}</h3>
                <p><strong>Latitude:</strong> ${satellite.orbit[0].lat}</p>
                <p><strong>Longitude:</strong> ${satellite.orbit[0].lon}</p>
                <p><strong>Altitude:</strong> ${satellite.orbit[0].alt} km</p>
            `;
        });

        viewer.screenSpaceEventHandler.setInputAction((click) => {
            const pickedObject = viewer.scene.pick(click.position);
            if (Cesium.defined(pickedObject) && pickedObject.id) {
                viewer.selectedEntity = pickedObject.id;
                pickedObject.id.label.show = true;
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        const anyChartExists = document.getElementById("cubeSatChart") ||
                       document.getElementById("altitudeChart") ||
                       document.getElementById("velocityChart");

        if (anyChartExists) {
          initializeCharts();
        }

        const heatmapContainer = document.getElementById("heatmapContainer");
        if (heatmapContainer) {
            initializeHeatmap();
        }

        // Add event listener for capture button
        const captureBtn = document.getElementById("capture-btn");
        const statusProgress = document.getElementById("status-progress");
        const statusText = document.getElementById("status-text");
        if (captureBtn) {
            captureBtn.addEventListener("click", async () => {
                const latInput = document.getElementById("latitude");
                const lonInput = document.getElementById("longitude");
                const datasetSelector = document.getElementById("datasetSelector");

                const latitude = parseFloat(latInput.value);
                const longitude = parseFloat(lonInput.value);
                const dataset = datasetSelector.value;

                if (isNaN(latitude) || latitude < -90 || latitude > 90) {
                    alert("Please enter a valid latitude between -90 and 90.");
                    return;
                }
                if (isNaN(longitude) || longitude < -180 || longitude > 180) {
                    alert("Please enter a valid longitude between -180 and 180.");
                    return;
                }

                try {
                    statusProgress.style.width = "0%";
                    statusText.textContent = "Starting image capture...";
                    // Simulate progress bar animation
                    let progress = 0;
                    const interval = setInterval(() => {
                        if (progress >= 90) {
                            clearInterval(interval);
                        } else {
                            progress += 10;
                            statusProgress.style.width = progress + "%";
                        }
                    }, 300);

                    const capturePromise = captureImage(latitude, longitude, dataset);
                    capturePromise.then(data => {
                        clearInterval(interval);
                        statusProgress.style.width = "100%";
                        statusText.textContent = "Image capture successful.";
                        alert("Image capture successful.");
                        if (data && data.rgb_url) {
                            console.log("Capture button handler received rgb_url:", data.rgb_url);
                            const normalizedRgbUrl = data.rgb_url.replace(/\\/g, '/');
                            const fullUrl = `${window.location.origin}/static/${normalizedRgbUrl}`;
                            console.log("Setting local_rgb_url in localStorage:", fullUrl);
                            window.localStorage.setItem('local_rgb_url', fullUrl);
                        } else {
                            console.warn("Capture button handler did not receive rgb_url in data:", data);
                        }
                    }).catch(error => {
                        clearInterval(interval);
                        statusProgress.style.width = "0%";
                        statusText.textContent = "Image capture failed.";
                        alert("Failed to capture image: " + error.message);
                    });
                } catch (error) {
                    statusProgress.style.width = "0%";
                    statusText.textContent = "Image capture failed.";
                    alert("Failed to capture image: " + error.message);
                }
            });
        }

    } catch (error) {
        console.error("Critical error in main.js:", error);
    }

    // Add event listener for classify button
    const classifyBtn = document.getElementById("classify-btn");
    if (classifyBtn) {
        classifyBtn.addEventListener("click", async () => {
            const rgbImage = document.getElementById("rgb-image");
            if (!rgbImage || !rgbImage.src) {
                alert("No RGB image available for classification.");
                return;
            }

                try {
                    // Use the full local_rgb_url stored after capture for classification
                    let imageUrl = window.localStorage.getItem('local_rgb_url');
                    console.log("Retrieved local_rgb_url from localStorage:", imageUrl);
                    if (!imageUrl) {
                        alert("No local RGB image URL found for classification.");
                        return;
                    }
                    // Extract relative path from full URL
                    try {
                        const urlObj = new URL(imageUrl);
                        imageUrl = urlObj.pathname.startsWith('/static/') ? urlObj.pathname.substring(8) : urlObj.pathname.substring(1);
                    } catch (e) {
                        // If not a valid URL, use as is
                    }
                    // Normalize backslashes to forward slashes
                    imageUrl = imageUrl.replace(/\\/g, '/');
                    // If imageUrl is empty after normalization, alert and return
                    if (!imageUrl) {
                        alert("Invalid local RGB image URL for classification.");
                        return;
                    }
                    // No fallback to rgbImage.src to avoid sending remote URLs

                const response = await fetch(`${BASE_URL}/classify_image`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ image_url: imageUrl }),
                });

                const data = await response.json();

                if (data.error) {
                    alert("Classification failed: " + data.error);
                    return;
                }

                const classificationResults = data.classification_percentages;
                const classificationList = document.getElementById("classification-list");
                classificationList.innerHTML = "";

                for (const [className, percentage] of Object.entries(classificationResults)) {
                    const li = document.createElement("li");
                    li.className = "list-group-item";
                    li.textContent = `${className}: ${percentage}%`;
                    classificationList.appendChild(li);
                }

                document.getElementById("classification-results").style.display = "block";
            } catch (error) {
                alert("Error during classification: " + error.message);
            }
        });
    }
});
