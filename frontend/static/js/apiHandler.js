export async function fetchCubeSatData(viewer) {
    try {
        const response = await fetch('http://127.0.0.1:5001/api/cubesat_positions');
        const data = await response.json();

        // Validate data
        if (!Array.isArray(data)) {
            throw new Error('Invalid data format: Expected an array');
        }

        data.forEach(sat => {
            if (typeof sat.lat !== 'number' || typeof sat.lon !== 'number' || typeof sat.alt !== 'number') {
                throw new Error('Invalid data format: Expected latitude, longitude, and altitude to be numbers');
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

export async function captureImage(latitude, longitude) {
    try {
        const response = await fetch('http://127.0.0.1:5001/api/capture_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ latitude, longitude }),
        });
        const data = await response.json();
        displayCapturedImage(data.image_url);
        storeImageInDatabase(data.image_url, latitude, longitude);
    } catch (error) {
        console.error('Error capturing image:', error);
    }
}

export async function fetchImageHistory() {
    try {
        const response = await fetch('http://127.0.0.1:5001/api/image_history');
        const data = await response.json();
        displayImageHistory(data);
    } catch (error) {
        console.error('Error fetching image history:', error);
    }
}

async function storeImageInDatabase(imageUrl, latitude, longitude) {
    try {
        await fetch('http://127.0.0.1:5001/api/store_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ imageUrl, latitude, longitude }),
        });
    } catch (error) {
        console.error('Error storing image in database:', error);
    }
}