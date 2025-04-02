const BASE_URL = 'http://127.0.0.1:5001/api';

/**
 * Fetch CubeSat positional data and update the Cesium viewer.
 */
export async function fetchCubeSatData(viewer) {
    try {
        const response = await fetch(`${BASE_URL}/cubesat_positions`);
        const data = await response.json();

        console.log("🚀 Received API Data:", data); // ✅ Log raw API response

        if (!Array.isArray(data)) {
            throw new Error('Invalid data format: Expected an array');
        }

        data.forEach(sat => {
            console.log("📡 Processing satellite:", sat); // ✅ Log each satellite entry

            if (sat.lat === undefined || sat.lon === undefined || sat.alt === undefined) {
                console.error('⚠️ Missing required fields:', sat);
                return;
            }

            if (isNaN(sat.lat) || isNaN(sat.lon) || isNaN(sat.alt)) {
                console.error('⚠️ Invalid number values:', sat);
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
        console.error('❌ Error fetching CubeSat data:', error);
    }
}

/**
 * Capture an image using CubeSat coordinates from Google Earth Engine.
 */
export async function captureImage(latitude, longitude) {
    try {
        const response = await fetch(`${BASE_URL}/capture_image`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude }),
        });

        const data = await response.json();
        console.log("📸 Capture Response:", data);

        if (!data.image_url) {
            throw new Error("🚨 No image URL received from API!");
        }

        // Display image immediately
        displayCapturedImage(data.image_url);

        // Store image in the database
        await storeImageInDatabase(data.image_url, latitude, longitude);
    } catch (error) {
        console.error('❌ Error capturing image:', error);
    }
}

/**
 * Fetch and display stored image history.
 */
export async function fetchImageHistory() {
    try {
        const response = await fetch(`${BASE_URL}/image_history`);
        const data = await response.json();

        console.log("🖼️ Image History Data:", data);

        if (!Array.isArray(data)) {
            throw new Error("Invalid image history format. Expected an array.");
        }

        if (data.length === 0) {
            console.warn("⚠️ No images found in history.");
        }

        displayImageHistory(data);
    } catch (error) {
        console.error('❌ Error fetching image history:', error);
    }
}

/**
 * Store the captured image URL in the database.
 */
async function storeImageInDatabase(imageUrl, latitude, longitude) {
    try {
        const response = await fetch(`${BASE_URL}/store_image`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ imageUrl, latitude, longitude }), // ✅ Fixed key names
        });

        const result = await response.json();
        console.log("✅ Image stored successfully:", result);
    } catch (error) {
        console.error('❌ Error storing image in database:', error);
    }
}
