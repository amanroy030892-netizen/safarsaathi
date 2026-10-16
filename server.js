/**
 * SafarSaathi Admin Ad Upload & Map Telemetry API Server
 * Node.js / Express Server for handling secure admin video ad uploads,
 * media file storage, and real-time GPS stream broadcast.
 */

const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// In-Memory & File Storage for Admin Sponsored Video Ads
const ADS_DB_FILE = path.join(__dirname, 'ads_data.json');

function loadAds() {
  try {
    if (fs.existsSync(ADS_DB_FILE)) {
      return JSON.parse(fs.readFileSync(ADS_DB_FILE, 'utf-8'));
    }
  } catch (e) {}
  return {
    src: 'promo_ad.mp4',
    title: 'SafarSaathi Premium Carpool Network',
    link: 'https://wa.me/916901027507',
    duration: 90,
    updatedAt: new Date().toISOString()
  };
}

function saveAds(adData) {
  try {
    fs.writeFileSync(ADS_DB_FILE, JSON.stringify(adData, null, 2), 'utf-8');
  } catch (e) {
    console.error('Error saving ads:', e);
  }
}

// 1. GET Current Video Ad for Customer Home Screen
app.get('/api/ads/current', (req, res) => {
  const currentAd = loadAds();
  res.json({ success: true, ad: currentAd });
});

// 2. POST Admin Video Ad Upload Endpoint (Strictly Protected by Admin PIN: 1432)
app.post('/api/admin/upload-ad', (req, res) => {
  const { adminPin, title, link, duration, videoBase64 } = req.body;

  if (adminPin !== '1432') {
    return res.status(403).json({ success: false, error: 'Unauthorized: Invalid Admin PIN' });
  }

  if (!videoBase64) {
    return res.status(400).json({ success: false, error: 'Video file payload is required' });
  }

  // Enforce Max 1.5 Minutes (90 Seconds) duration
  const adDuration = Math.min(parseInt(duration) || 90, 90);

  const newAd = {
    src: videoBase64,
    title: title || 'SafarSaathi Sponsored Video Ad',
    link: link || 'https://wa.me/916901027507',
    duration: adDuration,
    updatedAt: new Date().toISOString()
  };

  saveAds(newAd);
  console.log(`[Admin] Video Ad successfully updated by Admin: "${newAd.title}" (${adDuration}s)`);

  res.json({
    success: true,
    message: 'Video ad published successfully to all customer Home screens!',
    ad: newAd
  });
});

// 3. Real-Time Telemetry & Heading Stream Endpoint
app.post('/api/telemetry/stream', (req, res) => {
  const { userId, lat, lng, speed, heading, isDriving } = req.body;
  res.json({
    success: true,
    status: isDriving ? 'DRIVE_MODE' : (speed < 1.5 ? 'STATIONARY_POV' : 'WALKING'),
    speed: speed || 0,
    heading: heading || 0,
    timestamp: new Date().toISOString()
  });
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`SafarSaathi Server running on port ${PORT}`);
  });
}

module.exports = app;
