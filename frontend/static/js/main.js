import { initializeCesium } from "./cesiumSetup.js";
import { fetchCubeSatData, captureImage, fetchImageHistory } from "./apiHandler.js";
import { setupUIInteractions } from "./uiHandler.js";

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Cesium Viewer
    const viewer = initializeCesium();

    // Setup UI interactions
    setupUIInteractions(viewer, captureImage, fetchImageHistory);

    // Fetch and render CubeSat data
    fetchCubeSatData(viewer);
});