document.addEventListener('DOMContentLoaded', () => {
    const historyContainer = document.createElement('div');
    historyContainer.id = 'image-history-container';
    historyContainer.style.position = 'absolute';
    historyContainer.style.top = '10px';
    historyContainer.style.right = '10px';
    historyContainer.style.background = 'rgba(0, 0, 0, 0.7)';
    historyContainer.style.color = 'white';
    historyContainer.style.padding = '10px';
    historyContainer.style.display = 'none';
    document.body.appendChild(historyContainer);

    document.getElementById('imageHistory').addEventListener('click', () => {
        historyContainer.style.display = historyContainer.style.display === 'none' ? 'block' : 'none';
    });
});
