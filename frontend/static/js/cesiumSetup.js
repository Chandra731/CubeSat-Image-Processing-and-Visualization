import { BASE_URL } from './apiHandler.js';

Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlMjYwMDI1Zi1lZjQ0LTQwYWItOWVjZS0wMGI3NDY4MDdhMTYiLCJpZCI6Mjc5ODk1LCJpYXQiOjE3NDA5ODM4OTB9.eqghcb_A5OLI-XRfCBeWaH_BQfIXX8AX7kxO-VOcxGs';

export function initializeCesium() {
    const viewer = new Cesium.Viewer('cesiumContainer', {
        terrainProvider: Cesium.createWorldTerrain(),
        animation: false,
        timeline: false,
        sceneMode: Cesium.SceneMode.SCENE3D, // Ensure 3D mode is enabled
        baseLayerPicker: false, // Optional: Disable base layer picker for cleaner UI
        geocoder: true, // Enable geocoder to search for locations
        homeButton: true, // Enable home button to reset view
        sceneModePicker: true, // Enable scene mode picker to switch between 2D, 3D, and Columbus View
        navigationHelpButton: true, // Enable navigation help button
        infoBox: true, // Enable info box for detailed information
        fullscreenButton: true // Enable fullscreen button
    });

    const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction((movement) => {
        const cartesian = viewer.camera.pickEllipsoid(movement.endPosition, viewer.scene.globe.ellipsoid);
        if (cartesian) {
            const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
            const latitude = Cesium.Math.toDegrees(cartographic.latitude).toFixed(6);
            const longitude = Cesium.Math.toDegrees(cartographic.longitude).toFixed(6);
            document.getElementById('latitude').value = latitude;
            document.getElementById('longitude').value = longitude;
            document.getElementById('latitude-display').innerText = latitude;
            document.getElementById('longitude-display').innerText = longitude;
        }
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    fetch(`${BASE_URL}/cubesat_positions`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            data.forEach(sat => {
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
        })
        .catch(error => console.error('Error loading CubeSat data:', error));

    return viewer;
}
