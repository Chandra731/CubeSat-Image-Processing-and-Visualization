import { BASE_URL } from './apiHandler.js';

export function initializeHeatmap() {
    const map = L.map('heatmapContainer').setView([0, 0], 2);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Fetch CubeSat position data
    fetch(`${BASE_URL}/cubesat_positions`)
        .then(response => response.json())
        .then(data => {
            // Prepare heatmap points: [lat, lon, intensity]
            const heatmapData = data
                .filter(sat => sat.lat !== null && sat.lat !== undefined && sat.lon !== null && sat.lon !== undefined)
                .map(sat => [sat.lat, sat.lon, 0.6]);

            // Add heat layer
            L.heatLayer(heatmapData, {
                radius: 30,
                blur: 25,
                maxZoom: 8,
                gradient: {
                    0.2: 'blue',
                    0.4: 'lime',
                    0.6: 'yellow',
                    0.8: 'orange',
                    1.0: 'red'
                }
            }).addTo(map);

            // Add legend
            const legend = L.control({ position: 'bottomright' });

            legend.onAdd = function () {
                const div = L.DomUtil.create('div', 'info legend');
                const grades = [0.2, 0.4, 0.6, 0.8, 1.0];
                const labels = ['Low', '', 'Medium', '', 'High'];
                const colors = ['blue', 'lime', 'yellow', 'orange', 'red'];

                div.innerHTML += '<h6 class="text-center">Density</h6>';
                for (let i = 0; i < grades.length; i++) {
                    div.innerHTML += `
                        <i style="background:${colors[i]}; width:18px; height:18px; display:inline-block; margin-right:8px;"></i>
                        ${labels[i]}<br>`;
                }

                return div;
            };

            legend.addTo(map);
        })
        .catch(error => console.error('Error loading heatmap data:', error));
}
