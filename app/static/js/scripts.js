// Sidebar collapse toggle
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('sidebar-toggle');
toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

function toggleControlSidebar() {
    const sidebar = document.getElementById("control-sidebar");
    const overlay = document.getElementById("overlay");
    sidebar.classList.toggle("open");
    if (sidebar.classList.contains("open")) {
        overlay.style.display = "block";
    } else {
        overlay.style.display = "none";
    }
}

// Refresh CPU temp every 5s
setInterval(() => {
    fetch('/temperature')
        .then(res => res.text())
        .then(temp => {
            document.getElementById('cpu-temp').innerText = temp + '°C';
        });
}, 5000);