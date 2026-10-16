/**
 * SafarSaathi Map & Navigation Engine
 * 1. Default Mode: Drive Mode (3D Navigation Car Scene / Chevron Marker)
 * 2. Stationary / Stopped Mode (<1.5 km/h): Point of View (POV) 60° Compass Flashlight Cone
 * 3. Walking Mode (1.5 - 7 km/h): Directional Walking Arrow showing exact travel heading
 * 4. Driving Mode (>7 km/h): 3D Vehicle Navigation Scene with Road-Snap & Camera Follow
 */

let googleLiveMap = null;
let googleRoadLayer = null;
let googleSatelliteLayer = null;
let isGoogleSatelliteActive = false;
let userLiveGpsMarker = null;
let userGpsAccuracyCircle = null;
let activeCarMapMarkers = [];
let currentLiveCoords = null;

// 🧭 DRIVING NAVIGATION MODE STATE & BEARING ENGINE
let lastGpsCoords = null;
let lastGpsTimestamp = 0;
let currentVehicleSpeedKmH = 0;
let currentVehicleHeading = 0;
let isVehicleDrivingMode = true; // DRIVE MODE ACTIVE BY DEFAULT!

function calculateBearing(lat1, lon1, lat2, lon2) {
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const y = Math.sin(dLon) * Math.cos(lat2 * Math.PI / 180);
  const x = Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
            Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos(dLon);
  let brng = Math.atan2(y, x) * 180 / Math.PI;
  return Math.round((brng + 360) % 360);
}

function getCompassDirection(deg) {
  const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'];
  return directions[Math.round(deg / 45) % 8];
}

// Hardware Compass Listener (iOS & Android)
if (typeof window !== 'undefined' && window.DeviceOrientationEvent) {
  try {
    window.addEventListener('deviceorientation', function(e) {
      if (e.webkitCompassHeading) {
        currentVehicleHeading = Math.round(e.webkitCompassHeading);
      } else if (e.alpha !== null && e.absolute) {
        currentVehicleHeading = Math.round(360 - e.alpha);
      }
    }, true);
  } catch(e){}
}

function handleGpsPositionUpdate(pos, forceZoom) {
  const rawLat = pos.coords.latitude;
  const rawLng = pos.coords.longitude;
  const rawAccuracy = Math.round(pos.coords.accuracy || 8);
  const rawSpeed = (pos.coords.speed !== null && !isNaN(pos.coords.speed) && pos.coords.speed >= 0) ? pos.coords.speed : null;
  const rawHeading = (pos.coords.heading !== null && !isNaN(pos.coords.heading) && pos.coords.heading >= 0) ? pos.coords.heading : null;

  const now = Date.now();
  let calculatedSpeed = 0;
  let calculatedHeading = currentVehicleHeading;

  if (lastGpsCoords && lastGpsTimestamp) {
    const timeDiffSec = (now - lastGpsTimestamp) / 1000;
    const distM = typeof getHaversineDistanceKm === 'function' ? getHaversineDistanceKm(lastGpsCoords.lat, lastGpsCoords.lng, rawLat, rawLng) * 1000 : 0;
    if (timeDiffSec > 0.4) {
      calculatedSpeed = Math.round((distM / timeDiffSec) * 3.6);
      if (distM >= 3) {
        calculatedHeading = calculateBearing(lastGpsCoords.lat, lastGpsCoords.lng, rawLat, rawLng);
      }
    }
  }

  currentVehicleSpeedKmH = (rawSpeed !== null) ? Math.round(rawSpeed * 3.6) : calculatedSpeed;
  if (rawHeading !== null && !isNaN(rawHeading)) {
    currentVehicleHeading = Math.round(rawHeading);
  } else if (calculatedHeading !== null) {
    currentVehicleHeading = calculatedHeading;
  }

  // Drive Mode Active by Default (Transitions smoothly between Stationary POV, Walking, and Driving Car)
  isVehicleDrivingMode = true;

  lastGpsCoords = { lat: rawLat, lng: rawLng };
  lastGpsTimestamp = now;

  const lat = rawLat;
  const lng = rawLng;
  const accuracy = rawAccuracy;
  const roadName = 'Assam Live Corridor';

  currentLiveCoords = {
    lat,
    lng,
    rawLat,
    rawLng,
    accuracy,
    roadName,
    speed: currentVehicleSpeedKmH,
    heading: currentVehicleHeading,
    isDriving: isVehicleDrivingMode,
    lastUpdated: new Date().toISOString()
  };

  updateCoordsDisplay(lat, lng, accuracy, roadName, false);

  if (googleLiveMap && typeof L !== 'undefined') {
    updateUserMarkerOnMap(lat, lng, accuracy, roadName, forceZoom);
  }
}

function updateUserMarkerOnMap(lat, lng, accuracy, roadName, shouldZoom) {
  if (!googleLiveMap || typeof L === 'undefined') return;

  if (shouldZoom) {
    googleLiveMap.setView([lat, lng], 16);
  }

  // 🧭 GOOGLE MAPS NAVIGATION: DRIVE MODE BY DEFAULT • CAR SCENE • STATIONARY POV CONE • WALKING DIRECTION
  let markerHtml = '';
  const isStationary = (currentVehicleSpeedKmH < 1.5);
  const isWalking = (currentVehicleSpeedKmH >= 1.5 && currentVehicleSpeedKmH < 7.0);

  if (isStationary) {
    // 👁️ STATIONARY POINT OF VIEW (POV): Dynamic 60° Compass Field-of-View Cone radiating forward
    markerHtml = `
      <div style="position:relative; width:54px; height:54px; display:flex; align-items:center; justify-content:center;">
        <div style="position:absolute; width:54px; height:54px; transform: rotate(${currentVehicleHeading}deg); transition: transform 0.25s ease-out; pointer-events:none;">
          <svg viewBox="0 0 54 54" style="width:54px; height:54px;" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M27 27 L9 0 A34 34 0 0 1 45 0 Z" fill="url(#povGradient)" opacity="0.65"/>
            <defs>
              <linearGradient id="povGradient" x1="27" y1="27" x2="27" y2="0" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#16a34a" stop-opacity="0.85"/>
                <stop offset="100%" stop-color="#86efac" stop-opacity="0"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div style="position:absolute; width:34px; height:34px; border-radius:50%; background:rgba(22,163,74,0.3); animation:pulse 1.4s infinite;"></div>
        <div style="width:18px; height:18px; background:#16a34a; border:3px solid #ffffff; border-radius:50%; box-shadow:0 0 10px rgba(0,0,0,0.4); position:relative; z-index:2; display:flex; align-items:center; justify-content:center;">
          <div style="width:6px; height:6px; background:#ffffff; border-radius:50%;"></div>
        </div>
        <div style="position:absolute; bottom:-12px; background:#ffffff; color:#15803d; font-size:8.5px; font-weight:900; padding:1px 5px; border-radius:4px; border:1px solid #16a34a; white-space:nowrap; box-shadow:0 1px 4px rgba(0,0,0,0.15); z-index:3;">
          👁️ POV: ${getCompassDirection(currentVehicleHeading)}
        </div>
      </div>
    `;
  } else if (isWalking) {
    // 🚶 WALKING ON FOOT: Directional Chevron & Compass Beam showing walking path
    markerHtml = `
      <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
        <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(2,132,199,0.25); animation:pulse 1.2s infinite;"></div>
        <div style="transform: rotate(${currentVehicleHeading}deg); transition: transform 0.3s ease-out; display:flex; align-items:center; justify-content:center; filter: drop-shadow(0 3px 8px rgba(0,0,0,0.4));">
          <svg viewBox="0 0 36 36" style="width:36px; height:36px;" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 2L31 30L18 23L5 30L18 2Z" fill="#0284c7" stroke="#ffffff" stroke-width="2.2" stroke-linejoin="round"/>
            <path d="M18 2L31 30L18 23V2Z" fill="#0369a1"/>
            <circle cx="18" cy="20" r="3" fill="#ffffff"/>
          </svg>
        </div>
        <div style="position:absolute; bottom:-12px; background:#0284c7; color:#ffffff; font-size:8.5px; font-weight:900; padding:1px 5px; border-radius:4px; white-space:nowrap; box-shadow:0 1px 4px rgba(0,0,0,0.25);">
          🚶 ${currentVehicleSpeedKmH} km/h
        </div>
      </div>
    `;
  } else {
    // 🚗 CAR SCENE & DRIVE MODE (DEFAULT): 3D Navigation Vehicle Chevron in Travel Direction
    markerHtml = `
      <div style="position:relative; width:52px; height:52px; display:flex; align-items:center; justify-content:center;">
        <div style="position:absolute; width:50px; height:50px; border-radius:50%; background:rgba(22,163,74,0.32); animation:pulse 1.1s infinite;"></div>
        <div style="transform: rotate(${currentVehicleHeading}deg); transition: transform 0.3s cubic-bezier(0.2, 0, 0.2, 1); display:flex; align-items:center; justify-content:center; filter: drop-shadow(0 4px 10px rgba(0,0,0,0.5));">
          <svg viewBox="0 0 44 44" style="width:42px; height:42px;" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 22 L8 2 L36 2 Z" fill="#86efac" opacity="0.35"/>
            <path d="M22 4L37 36L22 29L7 36L22 4Z" fill="#16a34a" stroke="#ffffff" stroke-width="2.5" stroke-linejoin="round"/>
            <path d="M22 4L37 36L22 29V4Z" fill="#15803d"/>
            <circle cx="22" cy="26" r="3.5" fill="#ffffff"/>
          </svg>
        </div>
        <div style="position:absolute; bottom:-12px; background:#15803d; color:#ffffff; font-size:9px; font-weight:900; padding:1px 6px; border-radius:4px; box-shadow:0 2px 5px rgba(0,0,0,0.3); border:1px solid #86efac; white-space:nowrap;">
          🚗 ${currentVehicleSpeedKmH > 0 ? currentVehicleSpeedKmH + ' km/h' : 'DRIVE MODE'}
        </div>
      </div>
    `;
  }

  const userGpsIcon = L.divIcon({
    className: 'user-direct-live-pin',
    html: markerHtml,
    iconSize: [54, 54],
    iconAnchor: [27, 27]
  });

  if (!userLiveGpsMarker) {
    userLiveGpsMarker = L.marker([lat, lng], { icon: userGpsIcon, draggable: false }).addTo(googleLiveMap);
  } else {
    userLiveGpsMarker.setIcon(userGpsIcon);
    userLiveGpsMarker.setLatLng([lat, lng]);
  }

  if (isVehicleDrivingMode && googleLiveMap && !shouldZoom) {
    try {
      googleLiveMap.panTo([lat, lng], { animate: true, duration: 0.6 });
    } catch(e){}
  }
}

function updateCoordsDisplay(lat, lng, accuracy, roadName, isSnapped) {
  const coordsEl = document.getElementById('map-coords-display');
  if (!coordsEl) return;

  const isStationary = (currentVehicleSpeedKmH < 1.5);
  const isWalking = (currentVehicleSpeedKmH >= 1.5 && currentVehicleSpeedKmH < 7.0);

  if (isStationary) {
    coordsEl.innerHTML = `<span style="color:#15803d; font-weight:900;">👁️ Point of View (POV):</span> <b style="color:#000000;">Facing ${getCompassDirection(currentVehicleHeading)} (${currentVehicleHeading}°)</b> • <span style="color:#64748b;">Stationary</span>`;
  } else if (isWalking) {
    coordsEl.innerHTML = `<span style="color:#0284c7; font-weight:900;">🚶 Walking Direction:</span> <b style="color:#000000;">${currentVehicleSpeedKmH} km/h</b> • <span style="color:#0284c7; font-weight:800;">Heading ${getCompassDirection(currentVehicleHeading)} (${currentVehicleHeading}°)</span>`;
  } else {
    coordsEl.innerHTML = `<span style="color:#15803d; font-weight:900;">🚗 Drive Car Mode:</span> <b style="color:#000000;">${currentVehicleSpeedKmH} km/h</b> • <span style="color:#15803d; font-weight:800;">Heading ${getCompassDirection(currentVehicleHeading)} (${currentVehicleHeading}°)</span>`;
  }
}
