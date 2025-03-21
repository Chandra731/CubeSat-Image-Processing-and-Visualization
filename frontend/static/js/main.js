document.addEventListener('DOMContentLoaded', () => {
    const viewer = new Cesium.Viewer('earth-viewer', {
        imageryProvider: Cesium.createWorldImagery(), // Use default imagery provider
        baseLayerPicker: true,
        geocoder: true,
        sceneModePicker: true,
        timeline: true,
        animation: true,
    });

    viewer.homeButton.viewModel.command.beforeExecute.addEventListener(function (e) {
        e.cancel = true;
        viewer.camera.flyHome(2);
    });

    viewer.scene.camera.moveEnd.addEventListener(function () {
        const cameraPosition = viewer.camera.positionCartographic;
        console.log(`Latitude: ${Cesium.Math.toDegrees(cameraPosition.latitude)}, Longitude: ${Cesium.Math.toDegrees(cameraPosition.longitude)}`);
    });

    // Update input fields with latitude and longitude on mouse move
    viewer.screenSpaceEventHandler.setInputAction((movement) => {
        const cartesian = viewer.camera.pickEllipsoid(movement.endPosition);
        if (cartesian) {
            const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
            const latitude = Cesium.Math.toDegrees(cartographic.latitude);
            const longitude = Cesium.Math.toDegrees(cartographic.longitude);
            document.getElementById('latitude').value = latitude.toFixed(6);
            document.getElementById('longitude').value = longitude.toFixed(6);
        }
    }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

    viewer.screenSpaceEventHandler.setInputAction((event) => {
        const cartesian = viewer.camera.pickEllipsoid(event.position);
        if (cartesian) {
            const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
            const latitude = Cesium.Math.toDegrees(cartographic.latitude);
            const longitude = Cesium.Math.toDegrees(cartographic.longitude);

            // Capture image
            captureImage(latitude, longitude);
        }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    document.getElementById('capture-btn').addEventListener('click', () => {
        const latitude = document.getElementById('latitude').value;
        const longitude = document.getElementById('longitude').value;
        captureImage(latitude, longitude);
    });

    function captureImage(latitude, longitude) {
        fetch('/capture_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ latitude, longitude }),
        })
        .then(response => response.json())
        .then(data => {
            const imageDisplay = document.getElementById('image-display');
            imageDisplay.innerHTML = `
                <img src="${data.image_url}" alt="Satellite Image">
                <p>Classification: <strong>${data.classification}</strong></p>
                <p>Confidence: <strong>${data.confidence}%</strong></p>
            `;
            updateHistory(data);
        })
        .catch(error => console.error('Error capturing image:', error));
    }

    function updateHistory(data) {
        const historyList = document.getElementById('history-list');
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
            <img src="${data.image_url}" alt="Satellite Image" class="img-thumbnail">
            <div>
                <p>Classification: <strong>${data.classification}</strong></p>
                <p>Confidence: <strong>${data.confidence}%</strong></p>
            </div>
        `;
        historyList.appendChild(listItem);
    }

    // Fetch CubeSat positions
    fetch('/cubesat_positions')
        .then(response => response.json())
        .then(data => {
            console.log("CubeSat positions data:", data); // Log the data for debugging
            data.forEach(sat => {
                const position = Cesium.Cartesian3.fromDegrees(sat.lon, sat.lat, sat.alt * 1000);
                const satelliteEntity = viewer.entities.add({
                    position: position,
                    billboard: {
                        image: 'path/to/satellite-icon.png', // Path to your satellite icon
                        width: 32,
                        height: 32,
                    },
                    label: {
                        text: sat.satellite,
                        font: '14pt sans-serif',
                        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                        pixelOffset: new Cesium.Cartesian2(0, -20),
                    },
                    description: `
                        <table>
                            <tr><th>Satellite:</th><td>${sat.satellite}</td></tr>
                            <tr><th>Longitude:</th><td>${sat.lon}</td></tr>
                            <tr><th>Latitude:</th><td>${sat.lat}</td></tr>
                            <tr><th>Altitude:</th><td>${sat.alt} km</td></tr>
                        </table>
                    `
                });

                // Create a path for the orbit
                const orbitPositions = [];
                for (let i = 0; i < 360; i += 10) {
                    const radians = Cesium.Math.toRadians(i);
                    const orbitPosition = Cesium.Cartesian3.fromDegrees(
                        sat.lon + 0.1 * Math.cos(radians),
                        sat.lat + 0.1 * Math.sin(radians),
                        sat.alt * 1000
                    );
                    orbitPositions.push(orbitPosition);
                }
                viewer.entities.add({
                    polyline: {
                        positions: orbitPositions,
                        width: 2,
                        material: Cesium.Color.YELLOW,
                    }
                });
            });
        })
        .catch(error => console.error('Error fetching CubeSat positions:', error));
});