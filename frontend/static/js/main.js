document.addEventListener("DOMContentLoaded", function () {
    // Initialize Cesium Viewer
    const viewer = initializeCesium();

    // Setup UI interactions
    setupUIInteractions(viewer);

    // Fetch and render CubeSat data
    fetchCubeSatData(viewer);
});

function setupUIInteractions(viewer) {
    // Handle mouse move to update lat/lon input fields
    viewer.screenSpaceEventHandler.setInputAction((movement) => {
        const cartesian = viewer.camera.pickEllipsoid(movement.endPosition, viewer.scene.globe.ellipsoid);
        if (cartesian) {
            const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
            const latitude = Cesium.Math.toDegrees(cartographic.latitude).toFixed(6);
            const longitude = Cesium.Math.toDegrees(cartographic.longitude).toFixed(6);
            document.getElementById("latitude-input").value = latitude;
            document.getElementById("longitude-input").value = longitude;
        }
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    // Capture Image button click
    document.getElementById("capture-btn").addEventListener("click", function () {
        const lat = document.getElementById("latitude-input").value;
        const lon = document.getElementById("longitude-input").value;
        captureImage(lat, lon);
    });

    // Image History button click
    document.getElementById("image-history-btn").addEventListener("click", function () {
        fetchImageHistory();
    });
}

import { viewer, addHeatmapLayer, addSatellitePath } from "./cesiumSetup.js";
import { fetchCubesatPositions } from "./apiHandler.js";

async function initializeCubesats() {
    let satellites = await fetchCubesatPositions();

    satellites.forEach((sat) => {
        let position = Cesium.Cartesian3.fromDegrees(sat.lon, sat.lat, sat.alt);
        
        let entity = viewer.entities.add({
            name: sat.satellite,
            position: position,
            billboard: {
                image: "satellite_icon.png",
                scale: 0.6,
            },
            label: {
                text: sat.satellite,
                font: "14px sans-serif",
                fillColor: Cesium.Color.WHITE,
                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                outlineWidth: 2,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
            },
        });

        entity.description = `
            <h3>${sat.satellite}</h3>
            <p>Latitude: ${sat.lat.toFixed(2)}</p>
            <p>Longitude: ${sat.lon.toFixed(2)}</p>
            <p>Altitude: ${sat.alt.toFixed(2)} km</p>
        `;

        addSatellitePath(sat.satellite);
    });
}

// Initialize everything
initializeCubesats();
addHeatmapLayer();
