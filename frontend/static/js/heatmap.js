export function initializeHeatmap() {
    const map = L.map('heatmapContainer').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    fetch('http://127.0.0.1:5001/api/cubesat_positions')
        .then(response => response.json())
        .then(data => {
            const heatmapData = data.map(sat => [sat.lat, sat.lon, 0.5]);
            const heat = L.heatLayer(heatmapData, { radius: 25 }).addTo(map);
        })
        .catch(error => console.error('Error loading heatmap data:', error));
}