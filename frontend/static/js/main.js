import { initializeCesium } from "./cesiumSetup.js";
import { fetchCubeSatData, captureImage, fetchImageHistory } from "./apiHandler.js";
import { setupUIInteractions } from "./uiHandler.js";

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const viewer = initializeCesium();
        setupUIInteractions(viewer, captureImage, fetchImageHistory);
        await fetchCubeSatData(viewer);

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

        const ctx = document.getElementById("cubeSatChart")?.getContext("2d");
        if (ctx) {
            const cubeSatChart = new Chart(ctx, {
                type: "line",
                data: { labels: [], datasets: [{ label: "CubeSat Data", data: [], borderColor: "rgba(75, 192, 192, 1)", borderWidth: 1 }] },
                options: { scales: { y: { beginAtZero: true } } },
            });

            const chartResponse = await fetch("http://127.0.0.1:5001/api/cubesat_chart_data");
            const chartData = await chartResponse.json();

            if (chartData.labels && chartData.data) {
                cubeSatChart.data.labels = chartData.labels;
                cubeSatChart.data.datasets[0].data = chartData.data;
                cubeSatChart.update();
            }
        }

        const heatmapContainer = document.querySelector("#heatmapContainer");
        if (heatmapContainer && typeof h337 !== "undefined") {
            const heatmapInstance = h337.create({ container: heatmapContainer });
            const heatmapResponse = await fetch("http://127.0.0.1:5001/api/cubesat_heatmap_data");
            const heatmapData = await heatmapResponse.json();

            if (heatmapData.max !== undefined && Array.isArray(heatmapData.data)) {
                heatmapInstance.setData({ max: heatmapData.max, data: heatmapData.data });
            }
        }
    } catch (error) {
        console.error("Critical error in main.js:", error);
    }
});
