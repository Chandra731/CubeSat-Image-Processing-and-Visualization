Cesium.Ion.defaultAccessToken = 'YOUR_CESIUM_ION_ACCESS_TOKEN';

const viewer = new Cesium.Viewer('cesiumContainer', {
    terrainProvider: Cesium.createWorldTerrain(),
    animation: false,
    timeline: false
});

const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction((movement) => {
    const cartesian = viewer.camera.pickEllipsoid(movement.endPosition, viewer.scene.globe.ellipsoid);
    if (cartesian) {
        const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
        document.getElementById('latitude').value = Cesium.Math.toDegrees(cartographic.latitude).toFixed(4);
        document.getElementById('longitude').value = Cesium.Math.toDegrees(cartographic.longitude).toFixed(4);
    }
}, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

fetch('/api/cubesat_positions')
    .then(response => response.json())
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
                }
            });
        });
    })
    .catch(error => console.error('Error loading CubeSat data:', error));
