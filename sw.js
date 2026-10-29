/*
  SafarSaathi 24x7 Background Call, Lock-Screen Ringing & Auto-Purge Service Worker
  (Version: v115-background-voip-lockscreen-keepalive)
  Zero Stale Cache • Network-First No-Store • Background Call Wake-Up Engine
*/
const CACHE_NAME = 'safarsaathi-v115-background-voip-lockscreen-keepalive';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.map((k) => caches.delete(k)));
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || !event.request.url.startsWith('http')) return;

  event.respondWith(
    fetch(event.request, { cache: 'no-store' }).catch(() => {
      return caches.match(event.request);
    })
  );
});

// Listen for Background Call Alerts & Keep-Alive Pings from the App
self.addEventListener('message', (event) => {
  const data = event.data || {};
  if (data.type === 'SHOW_INCOMING_CALL_NOTIFICATION') {
    const pkt = data.packet || {};
    const veh = pkt.vehicleNumber || 'Live Vehicle';
    const title = '🔔 SafarSaathi Incoming Voice Call';
    const options = {
      body: `🔒 Verified Passenger is calling for ${veh} (Number Hidden). Tap to Accept & Talk!`,
      icon: 'icon-192.png',
      badge: 'icon-192.png',
      tag: 'safarsaathi-incoming-call',
      renotify: true,
      requireInteraction: true,
      vibrate: [500, 200, 500, 200, 500, 200, 800],
      data: { callId: pkt.callId || '', packet: pkt },
      actions: [
        { action: 'accept', title: '📞 Accept Call (उठाएं)' },
        { action: 'decline', title: '❌ Decline (काटें)' }
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

// Wake up / focus app window when Driver taps Lock-Screen Call Notification
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
        return self.clients.openWindow('./index.html?incoming_call_action=' + encodeURIComponent(action));
      }
    })
  );
});
