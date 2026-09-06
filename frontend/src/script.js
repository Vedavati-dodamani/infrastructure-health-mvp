const video = document.getElementById('video');
const startBtn = document.getElementById('startBtn');
const captureBtn = document.getElementById('captureBtn');
const fileInput = document.getElementById('fileInput');
const warnings = document.getElementById('warnings');
const resultsDiv = document.getElementById('results');
const canvas = document.getElementById('captureCanvas');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const drawCanvas = document.getElementById('drawCanvas');
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

let latestPreviewURL = null;

captureBtn.onclick = async () => {
  if (!video.srcObject) return alert('Start the camera first');
  const w = video.videoWidth; const h = video.videoHeight;
  canvas.width = w; canvas.height = h;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, w, h);
  canvas.toBlob(async (blob) => {
    if (latestPreviewURL) URL.revokeObjectURL(latestPreviewURL);
    latestPreviewURL = URL.createObjectURL(blob);
    previewImg.src = latestPreviewURL;
    imagePreview.style.display = 'block';
    setupDrawCanvas();

    const form = new FormData();
    form.append('file', blob, 'capture.jpg');
    resultsDiv.innerText = 'Uploading and analyzing...';
    const res = await fetch('/upload/image', { method: 'POST', body: form });
    if (!res.ok) {
      resultsDiv.innerText = 'Analysis failed';
      return;
    }
    const json = await res.json();
    renderAnalysis(json, latestPreviewURL);
  }, 'image/jpeg');
}

fileInput.onchange = async (e) => {
  const f = e.target.files[0];
  if (!f) return;
  if (latestPreviewURL) URL.revokeObjectURL(latestPreviewURL);
  latestPreviewURL = URL.createObjectURL(f);
  previewImg.src = latestPreviewURL;
  imagePreview.style.display = 'block';
  setupDrawCanvas();

  const form = new FormData();
  form.append('file', f);
  resultsDiv.innerText = 'Uploading and analyzing...';
  const res = await fetch('/upload/image', { method: 'POST', body: form });
  const json = await res.json();
  renderAnalysis(json, latestPreviewURL);
}

function renderAnalysis(payload, previewURL) {
  resultsDiv.innerHTML = '';
  const analysis = payload.analysis || payload;
  // show analysis mode
  const mode = document.createElement('div');
  mode.innerHTML = `<strong>Analysis mode:</strong> ${analysis.analysis_mode || 'unknown'}`;
  resultsDiv.appendChild(mode);
  const hdr = document.createElement('div');
  hdr.innerHTML = `<strong>Health score:</strong> ${analysis.health_score} <br/><strong>Status:</strong> ${analysis.status}`;
  resultsDiv.appendChild(hdr);
  const rec = document.createElement('div');
  rec.innerHTML = `<strong>Recommendations:</strong><ul>${analysis.recommendations.map(r=>`<li>${r}</li>`).join('')}</ul>`;
  resultsDiv.appendChild(rec);

  // detections list
  const list = document.createElement('div');
  if (analysis.detections && analysis.detections.length) {
    analysis.detections.forEach(d => {
      const el = document.createElement('div');
      el.className = 'detection';
      el.innerHTML = `<strong>${d.label}</strong> | severity: ${d.severity} | confidence: ${d.confidence}`;
      list.appendChild(el);
    });
  } else {
    list.innerText = 'No detections';
  }
  resultsDiv.appendChild(list);

  // draw bounding boxes on preview image if available
  if (previewURL && analysis.detections && analysis.detections.length) {
    drawDetectionsOnPreview(analysis.detections, analysis.image_shape);
  }
}

function setupDrawCanvas() {
  drawCanvas.width = previewImg.clientWidth;
  drawCanvas.height = previewImg.clientHeight;
  drawCanvas.style.width = previewImg.clientWidth + 'px';
  drawCanvas.style.height = previewImg.clientHeight + 'px';
}

function drawDetectionsOnPreview(detections, image_shape) {
  // wait for image to load
  if (!previewImg.complete) {
    previewImg.onload = () => drawDetectionsOnPreview(detections, image_shape);
    return;
  }
  const displayW = previewImg.clientWidth;
  const displayH = previewImg.clientHeight;
  const [origH, origW] = image_shape || [previewImg.naturalHeight, previewImg.naturalWidth];
  // scale factors
  const sx = displayW / origW;
  const sy = displayH / origH;
  drawCanvas.width = displayW;
  drawCanvas.height = displayH;
  drawCanvas.style.width = displayW + 'px';
  drawCanvas.style.height = displayH + 'px';
  const ctx = drawCanvas.getContext('2d');
  ctx.clearRect(0,0,drawCanvas.width, drawCanvas.height);
  detections.forEach(d => {
    const bx = d.bounding_box.x * sx;
    const by = d.bounding_box.y * sy;
    const bw = d.bounding_box.width * sx;
    const bh = d.bounding_box.height * sy;
    const color = severityColor(d.severity);
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(bx, by, bw, bh);
    ctx.fillStyle = color;
    ctx.font = '14px Arial';
    const label = `${d.label} (${Math.round(d.confidence*100)}%) - ${d.severity}`;
    ctx.fillText(label, bx + 4, by + 16);
  });
}

function severityColor(sev) {
  if (!sev) return '#00FF00';
  if (sev === 'Low') return '#2ECC71';
  if (sev === 'Medium') return '#F39C12';
  if (sev === 'High') return '#E74C3C';
  if (sev === 'Critical') return '#8B0000';
  return '#00FF00';
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
