import { BASE_URL } from './apiHandler.js';

export async function initializeCharts() {
    const cubeSatCtx = document.getElementById("cubeSatChart")?.getContext("2d");
    const altCtx = document.getElementById("altitudeChart")?.getContext("2d");
    const velCtx = document.getElementById("velocityChart")?.getContext("2d");

    // CubeSat Static Chart
    if (cubeSatCtx) {
        const cubeSatChart = new Chart(cubeSatCtx, {
            type: "line",
            data: {
                labels: [],
                datasets: [{
                    label: "CubeSat Data",
                    data: [],
                    borderColor: "rgba(75, 192, 192, 1)",
                    borderWidth: 1
                }]
            },
            options: { scales: { y: { beginAtZero: true } } }
        });

        try {
            const chartResponse = await fetch(`${BASE_URL}/cubesat_chart_data`);
            const chartData = await chartResponse.json();
            if (chartData.labels && chartData.data) {
                cubeSatChart.data.labels = chartData.labels;
                cubeSatChart.data.datasets[0].data = chartData.data;
                cubeSatChart.update();
            }
        } catch (error) {
            console.error("Error loading static chart data:", error);
        }
    }
    

    // Altitude and Velocity Charts from Orbit Data
    if (altCtx || velCtx) {
        try {
            const response = await fetch(`${BASE_URL}/cubesat_orbits`);
            const data = await response.json();

        if (!data.orbit || !Array.isArray(data.orbit)) {
            throw new Error("Invalid orbit data received from the server.");
        }

        const orbitData = data.orbit;


            // Velocity vs Time
            const velocityData = [];
            for (let i = 1; i < orbitData.length; i++) {
                const prev = orbitData[i - 1];
                const curr = orbitData[i];
                const timeDiffSec = (new Date(curr.timestamp) - new Date(prev.timestamp)) / 1000;
                const altDiff = curr.alt - prev.alt;
                const velocity = timeDiffSec !== 0 ? Math.abs(altDiff / timeDiffSec) : 0;
                velocityData.push({
                    x: new Date(curr.timestamp),
                    y: velocity
                });
            }

            // Render Altitude Chart
            if (altCtx) {
                new Chart(altCtx, {
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
                        responsive: true,
                        scales: {
                            x: {
                                type: 'time',
                                time: { unit: 'minute' },
                                title: { display: true, text: 'Time' }
                            },
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Altitude (km)' }
                            }
                        }
                    }
                });
            }

            // Render Velocity Chart
            if (velCtx) {
                new Chart(velCtx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: 'Estimated Velocity vs Time',
                            data: velocityData,
                            borderColor: 'rgba(153, 102, 255, 1)',
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: {
                                type: 'time',
                                time: { unit: 'minute' },
                                title: { display: true, text: 'Time' }
                            },
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Velocity (km/s)' }
                            }
                        }
                    }
                });
            }

        } catch (error) {
            console.error("Error loading orbit chart data:", error);
        }
    }
}
