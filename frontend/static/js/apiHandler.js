document.getElementById('capture').addEventListener('click', async () => {
    const latitude = document.getElementById('latitude').value;
    const longitude = document.getElementById('longitude').value;

    const response = await fetch('/api/capture_image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude, longitude })
    });

    const result = await response.json();
    alert(`Image Captured! URL: ${result.image_url}`);
});

document.getElementById('imageHistory').addEventListener('click', async () => {
    const response = await fetch('/api/image_history');
    const images = await response.json();

    let historyHTML = '<h3>Image History</h3><ul>';
    images.forEach(img => {
        historyHTML += `<li><a href="${img.image_url}" target="_blank">${img.timestamp}</a></li>`;
    });
    historyHTML += '</ul>';

    document.getElementById('image-history-container').innerHTML = historyHTML;
});
