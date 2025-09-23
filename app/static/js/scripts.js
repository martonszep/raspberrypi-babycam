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

// Refresh system metrics every 5s
function updateMetrics() {
  fetch("/metrics")
    .then(res => res.json())
    .then(data => {
      document.getElementById("cpu-temp").innerText = data.cpu_temp;
      document.getElementById("cpu-load").innerText = data.cpu_load;
      document.getElementById("ram-used").innerText = data.ram.used;
      document.getElementById("ram-total").innerText = data.ram.total;
      document.getElementById("ram-percent").innerText = data.ram.percent;
      const throttleEl = document.getElementById("throttle-status");
      if(data.throttle.error) {
        throttleEl.innerText = data.throttle.error;
      } else {
        if(data.throttle.active_issues.length === 0) {
          throttleEl.innerText = "No active issues (" + data.throttle.raw + ")";
        } else {
          throttleEl.innerText = data.throttle.active_issues.join("; ") + " (" + data.throttle.raw + ")";
        }
      }
    });
}
setInterval(updateMetrics, 5000);

document.addEventListener('DOMContentLoaded', () => {
    const audioEnabled = JSON.parse("{{ 'true' if audio_enabled else 'false' }}");
    const iframe = document.getElementById('video-iframe');

    if (iframe && audioEnabled) {
        try {
            iframe.muted = false;
        } catch(e) {
            console.warn('Cannot unmute iframe directly in this browser.');
        }
    }
});
