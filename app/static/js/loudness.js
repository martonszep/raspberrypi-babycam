// loudness.js
const DB_POLL_INTERVAL = 1000;
const chartCanvas = document.getElementById('loudness-chart');
const chartCtx = chartCanvas.getContext('2d');
let history = []; // array of numbers (dB)

function drawChart() {
    const ctx = chartCtx;
    const W = chartCanvas.width, H = chartCanvas.height;
    ctx.clearRect(0,0,W,H);
    // background
    ctx.fillStyle = '#111';
    ctx.fillRect(0,0,W,H);
    // grid
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.beginPath();
    for (let i=0;i<4;i++) {
        let y = (i+1) * H/5;
        ctx.moveTo(0,y); ctx.lineTo(W,y);
    }
    ctx.stroke();
    // draw line
    ctx.strokeStyle = '#2ecc71';
    ctx.lineWidth = 2;
    ctx.beginPath();
    const maxPoints = 60;
    const step = W / maxPoints;
    for (let i=0;i<maxPoints;i++){
        const v = history[i] ?? -120;
        const y = H - ((v + 120) / 120) * H; // map -120..0 to H..0
        const x = i * step;
        if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.stroke();
}

function updateLoudnessUI(db, historyArr){
    const dbEl = document.getElementById('loudness-db');
    if(dbEl) dbEl.innerText = db.toFixed(1);
    history = historyArr.slice(-60).map(h => h.db);
    // pad to 60 length
    while(history.length < 60) history.unshift(-120);
    drawChart();
}

async function pollLoudness(){
    try{
        const res = await fetch('/loudness');
        const j = await res.json();
        updateLoudnessUI(j.db, j.history || []);
    }catch(e){
        console.warn('loudness fetch error', e);
    } finally {
        setTimeout(pollLoudness, DB_POLL_INTERVAL);
    }
}

document.addEventListener('DOMContentLoaded', ()=>{
    pollLoudness();
});
