import { initializeCesium } from "./cesiumSetup.js";
import { fetchCubeSatData, captureImage, fetchImageHistory } from "./apiHandler.js";
import { setupUIInteractions } from "./uiHandler.js";

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize Cesium Viewer
        const viewer = initializeCesium();

        // Setup UI interactions
        setupUIInteractions(viewer, captureImage, fetchImageHistory);

        // Fetch and render CubeSat data
        await fetchCubeSatData(viewer);

        // Initialize Chart.js
        const ctx = document.getElementById('cubeSatChart')?.getContext('2d');
        if (!ctx) {
            console.warn("Chart element not found! Skipping Chart.js initialization.");
            return;
        }

        const cubeSatChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [], // Add labels dynamically
                datasets: [{
                    label: 'CubeSat Data',
                    data: [], // Add data dynamically
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });

        // Fetch CubeSat data for Chart.js
        fetch('http://127.0.0.1:5001/api/cubesat_chart_data')
            .then(response => response.json())
            .then(data => {
                if (data.labels && data.data) {
                    cubeSatChart.data.labels = data.labels;
                    cubeSatChart.data.datasets[0].data = data.data;
                    cubeSatChart.update();
                } else {
                    console.warn("Invalid CubeSat chart data format:", data);
                }
            })
            .catch(error => console.error('Error fetching CubeSat chart data:', error));

        // Initialize Heatmap.js
        const heatmapContainer = document.querySelector('#heatmapContainer');
        if (!heatmapContainer) {
            console.warn("Heatmap container not found! Skipping Heatmap.js initialization.");
            return;
        }

        const heatmapInstance = h337.create({ container: heatmapContainer });

        fetch('http://127.0.0.1:5001/api/cubesat_heatmap_data')
            .then(response => response.json())
            .then(data => {
                if (data.max !== undefined && Array.isArray(data.data)) {
                    heatmapInstance.setData({
                        max: data.max,
                        data: data.data
                    });
                } else {
                    console.warn("Invalid CubeSat heatmap data format:", data);
                }
            })
            .catch(error => console.error('Error fetching CubeSat heatmap data:', error));

    } catch (error) {
        console.error('Critical error in main.js:', error);
    }
});
