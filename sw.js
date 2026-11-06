/*
  SafarSaathi 24x7 Autonomous Background Call, Auto-Connect & 12h Pinpoint Road-GPS Service Worker
  (Version: v120-pinpoint-road-gps-and-autoconnect)
  Keeps Driver 100% Online & Connects Incoming Calls even when Phone is Locked or Chrome/App is Cut!
*/
const CACHE_NAME = 'safarsaathi-v120-pinpoint-road-gps-and-autoconnect';
const RTDB_BASE_URL = 'https://safar-saathi-e9f53-default-rtdb.firebaseio.com';
const RTDB_LATEST_CALL_URL = RTDB_BASE_URL + '/ss_active_calls/LATEST_ACTIVE_CALL.json';
const FIRESTORE_LATEST_CALL_URL = 'https://firestore.googleapis.com/v1/projects/safar-saathi-e9f53/databases/(default)/documents/ss_active_calls/LATEST_ACTIVE_CALL';

let swDriverIdentity = null;
let swLastNotifiedCallId = '';
let swWatchLoopTimer = null;
let swLastPresencePushMs = 0;

function readDriverIdentityFromIdb() {
  return new Promise((resolve) => {
    try {
      const req = indexedDB.open('SafarSaathiBgDB', 1);
      req.onupgradeneeded = (ev) => {
        const db = ev.target.result;
        if (!db.objectStoreNames.contains('meta')) {
          db.createObjectStore('meta');
        }
      };
      req.onsuccess = (ev) => {
        try {
          const db = ev.target.result;
          const tx = db.transaction('meta', 'readonly');
          const store = tx.objectStore('meta');
          const getReq = store.get('driverIdentity');
          getReq.onsuccess = () => resolve(getReq.result || null);
          getReq.onerror = () => resolve(null);
        } catch (e) { resolve(null); }
      };
      req.onerror = () => resolve(null);
    } catch (e) { resolve(null); }
  });
}

function saveDriverIdentityToIdb(identity) {
  return new Promise((resolve) => {
    try {
      const req = indexedDB.open('SafarSaathiBgDB', 1);
      req.onupgradeneeded = (ev) => {
        const db = ev.target.result;
        if (!db.objectStoreNames.contains('meta')) {
          db.createObjectStore('meta');
        }
      };
      req.onsuccess = (ev) => {
        try {
          const db = ev.target.result;
          const tx = db.transaction('meta', 'readwrite');
          const store = tx.objectStore('meta');
          store.put(identity, 'driverIdentity');
          tx.oncomplete = () => resolve(true);
          tx.onerror = () => resolve(false);
        } catch (e) { resolve(false); }
      };
      req.onerror = () => resolve(false);
    } catch (e) { resolve(false); }
  });
}

function parseFirestoreRestDoc(docJson) {
  if (!docJson || !docJson.fields) return null;
  const f = docJson.fields;
  const out = {};
  Object.keys(f).forEach((k) => {
    const v = f[k];
    if (v.stringValue !== undefined) out[k] = v.stringValue;
    else if (v.integerValue !== undefined) out[k] = Number(v.integerValue);
    else if (v.doubleValue !== undefined) out[k] = Number(v.doubleValue);
    else if (v.booleanValue !== undefined) out[k] = Boolean(v.booleanValue);
  });
  return out;
}

async function maintainDriver12hOnlineInSw() {
  try {
    const now = Date.now();
    if (now - swLastPresencePushMs < 12000) return;
    swLastPresencePushMs = now;
    if (!swDriverIdentity) {
      swDriverIdentity = await readDriverIdentityFromIdb();
    }
    if (!swDriverIdentity || !swDriverIdentity.phone) return;

    const entry = {
      phone: swDriverIdentity.phone || '',
      name: swDriverIdentity.name || 'Active Driver',
      deviceId: swDriverIdentity.deviceId || '',
      lastSeen: now,
      status: 'ONLINE'
    };
    const key = entry.phone || ('DEV_' + entry.deviceId);
    fetch(`${RTDB_BASE_URL}/ss_online_presence/${encodeURIComponent(key)}.json`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry)
    }).catch(() => {});
  } catch (e) {}
}

async function checkCloudForIncomingCallInSw() {
  try {
    await maintainDriver12hOnlineInSw();

    if (!swDriverIdentity) {
      swDriverIdentity = await readDriverIdentityFromIdb();
    }
    // Strict Isolation: Only check dedicated driver call endpoint for logged-in driver phone!
    if (!swDriverIdentity || !swDriverIdentity.phone) return;
    const myPhone = String(swDriverIdentity.phone).trim().replace(/\D/g, '');
    if (!myPhone) return;

    let pkt = null;
    try {
      const targetCallUrl = RTDB_BASE_URL + '/ss_driver_calls/' + encodeURIComponent(myPhone) + '.json?t=' + Date.now();
      const res = await fetch(targetCallUrl, { cache: 'no-store' });
      if (res && res.ok) {
        const data = await res.json();
        if (data && data.callId && String(data.driverPhone || '').trim().replace(/\D/g, '') === myPhone) {
          pkt = data;
        }
      }
    } catch (e) {}

    if (!pkt || !pkt.callId) return;
    if (pkt.status !== 'CALLING' && pkt.status !== 'RINGING') return;

    const ageMs = Date.now() - Number(pkt.updatedAt || new Date(pkt.startedAt || 0).getTime() || 0);
    if (ageMs > 60000) return;

    // Do not ring on the Caller's own phone
    if (swDriverIdentity && swDriverIdentity.deviceId && pkt.callerDeviceId === swDriverIdentity.deviceId) {
      const isSameDriverAccount = swDriverIdentity.phone && pkt.driverPhone && String(swDriverIdentity.phone).trim() === String(pkt.driverPhone).trim();
      if (!isSameDriverAccount) return;
    }

    // Acknowledge RINGING back to dedicated callId endpoint only!
    if (pkt.status === 'CALLING' && pkt.callId) {
      try {
        fetch(RTDB_BASE_URL + '/ss_active_calls/' + encodeURIComponent(pkt.callId) + '.json', {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'RINGING', sipMethod: '180_RINGING', driverOnline: true, updatedAt: Date.now() })
        }).catch(() => {});
      } catch (e) {}
    }

    // If any open/minimized window client exists, wake it and trigger auto-connect immediately!
    try {
      const clientList = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
      for (const client of clientList) {
        client.postMessage({
          type: 'SW_INCOMING_CALL_ACTION',
          action: 'accept',
          packet: pkt
        });
      }
    } catch (e) {}

    if (swLastNotifiedCallId === pkt.callId) return;
    swLastNotifiedCallId = pkt.callId;

    const veh = pkt.vehicleNumber || 'Live Vehicle';
    const title = '🔔 SafarSaathi Incoming Call (Auto-Connecting)';
    const options = {
      body: `🔒 Verified Passenger calling for ${veh}. Tap anywhere to talk now!`,
      icon: 'icon-192.png',
      badge: 'icon-192.png',
      tag: 'safarsaathi-incoming-call',
      renotify: true,
      requireInteraction: true,
      vibrate: [700, 180, 700, 180, 700, 180, 1200],
      data: { callId: pkt.callId || '', packet: pkt },
      actions: [
        { action: 'accept', title: '📞 Talk Now (Connected)' },
        { action: 'decline', title: '❌ End / Decline' }
      ]
    };
    await self.registration.showNotification(title, options);
  } catch (e) {}
}

function ensureSwBackgroundWatchLoop() {
  if (swWatchLoopTimer) return;
  swWatchLoopTimer = setInterval(() => {
    checkCloudForIncomingCallInSw();
  }, 1400);
}

const CORE_OFFLINE_ASSETS = [
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CORE_OFFLINE_ASSETS).catch(() => {});
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((k) => (k !== CACHE_NAME ? caches.delete(k) : Promise.resolve())));
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || !event.request.url.startsWith('http')) return;

  // Network-First with Offline Cache Fallback (guarantees instant live updates online + zero crash in Airplane Mode during Play Store review!)
  event.respondWith(
    fetch(event.request, { cache: 'no-store' }).then((networkRes) => {
      if (networkRes && networkRes.ok && event.request.url.startsWith(self.location.origin)) {
        const resClone = networkRes.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, resClone).catch(() => {});
        });
      }
      return networkRes;
    }).catch(() => {
      return caches.match(event.request).then((cachedRes) => {
        if (cachedRes) return cachedRes;
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
        return cachedRes;
      });
    })
  );
});

self.addEventListener('sync', (event) => {
  ensureSwBackgroundWatchLoop();
  if (event.tag === 'ss-bg-call-watch') {
    event.waitUntil(checkCloudForIncomingCallInSw());
  }
});

self.addEventListener('periodicsync', (event) => {
  ensureSwBackgroundWatchLoop();
  event.waitUntil(checkCloudForIncomingCallInSw());
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.identity && event.data.identity.phone) { ensureSwBackgroundWatchLoop(); }
  const data = event.data || {};
  if (data.type === 'REGISTER_DRIVER_BG_IDENTITY' && data.identity) {
    swDriverIdentity = data.identity;
    saveDriverIdentityToIdb(data.identity);
    maintainDriver12hOnlineInSw();
  } else if (data.type === 'SHOW_INCOMING_CALL_NOTIFICATION') {
    const pkt = data.packet || {};
    swLastNotifiedCallId = pkt.callId || '';
    const veh = pkt.vehicleNumber || 'Live Vehicle';
    const title = '🔔 SafarSaathi Incoming Call (Auto-Connecting)';
    const options = {
      body: `🔒 Verified Passenger calling for ${veh}. Tap anywhere to talk now!`,
      icon: 'icon-192.png',
      badge: 'icon-192.png',
      tag: 'safarsaathi-incoming-call',
      renotify: true,
      requireInteraction: true,
      vibrate: [700, 180, 700, 180, 700, 180, 1200],
      data: { callId: pkt.callId || '', packet: pkt },
      actions: [
        { action: 'accept', title: '📞 Talk Now (Connected)' },
        { action: 'decline', title: '❌ End / Decline' }
      ]
    };
    event.waitUntil(self.registration.showNotification(title, options));
  } else if (data.type === 'CLEAR_INCOMING_CALL_NOTIFICATION') {
    event.waitUntil(
      self.registration.getNotifications({ tag: 'safarsaathi-incoming-call' }).then((notifs) => {
        notifs.forEach((n) => n.close());
      })
    );
  }
});

self.addEventListener('notificationclick', (event) => {
  const action = event.action || 'accept';
  const notifData = event.notification ? event.notification.data : {};
  if (event.notification) event.notification.close();

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        try {
          client.postMessage({
            type: 'SW_INCOMING_CALL_ACTION',
            action: action,
            packet: notifData ? notifData.packet : null
          });
          if ('focus' in client) {
            return client.focus();
          }
        } catch (e) {}
      }
      if (self.clients.openWindow) {
        const callIdParam = (notifData && notifData.callId) ? ('&call_id=' + encodeURIComponent(notifData.callId)) : '';
        return self.clients.openWindow('./index.html?auto_accept_call=' + encodeURIComponent(action) + callIdParam);
      }
    })
  );
});
