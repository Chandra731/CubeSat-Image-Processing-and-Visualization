export function setupUIInteractions(viewer, captureImage, fetchImageHistory) {
    // Handle mouse move to update lat/lon input fields
    viewer.screenSpaceEventHandler.setInputAction((movement) => {
        const cartesian = viewer.camera.pickEllipsoid(movement.endPosition, viewer.scene.globe.ellipsoid);
        if (cartesian) {
            const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
            const latitude = Cesium.Math.toDegrees(cartographic.latitude).toFixed(6);
            const longitude = Cesium.Math.toDegrees(cartographic.longitude).toFixed(6);
            document.getElementById("latitude").value = latitude;
            document.getElementById("longitude").value = longitude;
            document.getElementById('latitude-display').innerText = latitude;
            document.getElementById('longitude-display').innerText = longitude;
        }
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    // Capture Image button click
    document.getElementById("capture-btn").addEventListener("click", function () {
        const lat = document.getElementById("latitude").value;
        const lon = document.getElementById("longitude").value;
        captureImage(lat, lon);
    });

    // Image History button click
    document.getElementById("image-history-btn").addEventListener("click", function () {
        fetchImageHistory();
    });
}

function displayCapturedImage(imageUrl) {
    const imageDisplay = document.getElementById('image-display');
    imageDisplay.innerHTML = `<img src="${imageUrl}" alt="Captured Image" class="img-thumbnail">`;
}

function displayImageHistory(data) {
    const historyContent = document.getElementById('image-history-content');
    historyContent.innerHTML = '';
    data.forEach(image => {
        const imageElement = document.createElement('div');
        imageElement.className = 'p-2';
        imageElement.innerHTML = `<img src="${image.image_url}" alt="Satellite Image" class="img-thumbnail">`;
        historyContent.appendChild(imageElement);
    });
    $('#image-history-modal').modal('show');
}