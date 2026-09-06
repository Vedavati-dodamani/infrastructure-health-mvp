// Map adapter using Leaflet fallback

async function initMap() {
  const map = L.map('map').setView([22.0, 78.0], 5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
  }).addTo(map);
  // load seeded assets
  try {
    const res = await fetch('/assets');
    const geojson = await res.json();
    L.geoJSON(geojson, {
      onEachFeature: (f, layer) => {
        if (f.properties && f.properties.name) {
          layer.bindPopup(`<strong>${f.properties.name}</strong><br/>${f.properties.type || ''}`);
        }
      }
    }).addTo(map);
  } catch (err) {
    console.warn('Could not load assets', err);
  }
}

window.addEventListener('load', initMap);
