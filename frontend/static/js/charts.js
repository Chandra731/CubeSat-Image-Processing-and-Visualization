export function initializeCharts() {
    fetch('http://127.0.0.1:5001/api/cubesat_positions')
        .then(response => response.json())
        .then(data => {
            const ctxAltitude = document.getElementById('altitudeChart').getContext('2d');
            const ctxVelocity = document.getElementById('velocityChart').getContext('2d');

            const altitudeData = data.map(sat => ({ x: new Date(sat.timestamp), y: sat.alt }));
            const velocityData = data.map(sat => ({ x: new Date(sat.timestamp), y: sat.velocity }));

            new Chart(ctxAltitude, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Altitude vs Time',
                        data: altitudeData,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        fill: true
                    }]
                },
                options: {
                    scales: {
                        x: { type: 'time', time: { unit: 'minute' } },
                        y: { beginAtZero: true }
                    }
                }
            });

            new Chart(ctxVelocity, {
                type: 'line',
                data: {
                    datasets: [{
                        label: 'Velocity vs Time',
                        data: velocityData,
                        borderColor: 'rgba(153, 102, 255, 1)',
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        fill: true
                    }]
                },
                options: {
                    scales: {
                        x: { type: 'time', time: { unit: 'minute' } },
                        y: { beginAtZero: true }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading chart data:', error));
}