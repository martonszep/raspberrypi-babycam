// Refresh CPU temperature every 5 seconds
setInterval(() => {
    fetch('/temperature')
        .then(response => response.text())
        .then(temp => {
            document.getElementById('cpu-temp').innerText = temp + '°C';
        });
}, 5000);