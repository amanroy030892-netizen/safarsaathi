/*
  SafarSaathi Ultra-Fast Real-Time Service Worker v20
  Zero Stale Cache • Network-First for Instant Real-Time Sync
*/
const CACHE_NAME = 'safarsaathi-v20-realtime-engine';

const PRECACHE_ASSETS = [
  './',
  './index.html',
  './admin.html',
  './privacy.html',
  './manifest.json',
  './car-bg.jpg',
  './car-bg.png',
  './icon-192.png',
  './icon-192-maskable.png',
  './icon-512.png',
  './icon-512-maskable.png',
  './safarsaathi_app_logo_1024.png',
  './feature-graphic-1024x500.png'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW v20] Pre-caching core assets');
      return cache.addAll(PRECACHE_ASSETS).catch((err) => {
        console.warn('[SW v20] Pre-cache partial fail (non-blocking):', err);
      });
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          console.log('[SW v20] Purging old cache:', cache);
          return caches.delete(cache);
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET' || !event.request.url.startsWith('http')) return;

  // Strict Network-First Strategy: Never serve stale HTML/JS
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          if (event.request.mode === 'navigate') {
            return caches.match('./index.html') || caches.match('./') || caches.match('/index.html') || caches.match('/');
          }
        });
      })
  );
});
