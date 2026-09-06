const video = document.getElementById('video');
const startBtn = document.getElementById('startBtn');
const captureBtn = document.getElementById('captureBtn');
const fileInput = document.getElementById('fileInput');
const warnings = document.getElementById('warnings');
const resultsDiv = document.getElementById('results');
const canvas = document.getElementById('captureCanvas');
let stream = null;

startBtn.onclick = async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('getUserMedia not supported in this browser');
    return;
  }
  stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
  video.srcObject = stream;
  startSimulatedFrameChecks();
}

captureBtn.onclick = async () => {
  if (!video.srcObject) return alert('Start the camera first');
  const w = video.videoWidth; const h = video.videoHeight;
  canvas.width = w; canvas.height = h;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, w, h);
  canvas.toBlob(async (blob) => {
    const form = new FormData();
    form.append('file', blob, 'capture.jpg');
    resultsDiv.innerText = 'Uploading and analyzing...';
    const res = await fetch('/upload/image', { method: 'POST', body: form });
    if (!res.ok) {
      resultsDiv.innerText = 'Analysis failed';
      return;
    }
    const json = await res.json();
    renderAnalysis(json);
  }, 'image/jpeg');
}

fileInput.onchange = async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  const form = new FormData();
  form.append('file', f);
  resultsDiv.innerText = 'Uploading and analyzing...';
  const res = await fetch('/upload/image', { method: 'POST', body: form });
  const json = await res.json();
  renderAnalysis(json);
}

function renderAnalysis(payload) {
  resultsDiv.innerHTML = '';
  if (payload.analysis && payload.analysis.detections) {
    const hdr = document.createElement('div');
    hdr.innerHTML = `<strong>Health score:</strong> ${payload.analysis.health_score} <br/><strong>Status:</strong> ${payload.analysis.status}`;
    resultsDiv.appendChild(hdr);
    const list = document.createElement('div');
    payload.analysis.detections.forEach(d => {
      const el = document.createElement('div');
      el.className = 'detection';
      el.innerText = `${d.type} | severity: ${d.severity} | confidence: ${d.confidence}`;
      list.appendChild(el);
    });
    resultsDiv.appendChild(list);
  } else {
    resultsDiv.innerText = JSON.stringify(payload, null, 2);
  }
}

// Simulated frame checks: sample a frame every second and show a random warning occasionally
let frameInterval = null;
function startSimulatedFrameChecks() {
  if (frameInterval) clearInterval(frameInterval);
  frameInterval = setInterval(() => {
    // draw small analysis overlay
    const chance = Math.random();
    warnings.innerText = '';
    if (chance < 0.15) {
      const w = document.createElement('div');
      w.className = 'warn';
      w.innerText = 'Warning: possible crack detected (simulated)';
      warnings.appendChild(w);
    } else if (chance < 0.35) {
      const w = document.createElement('div');
      w.className = 'info';
      w.innerText = 'Info: monitoring...';
      warnings.appendChild(w);
    }
  }, 1000);
}
