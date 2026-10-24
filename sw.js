/*
  SafarSaathi AI Auto-Purge Service Worker (Version: v110-live-moving-erickshaw-no-fare)
  Zero Stale Cache • Network-First No-Store • Chrome & Safari Compatible
*/
const CACHE_NAME = 'safarsaathi-v110-live-moving-erickshaw-no-fare';

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
