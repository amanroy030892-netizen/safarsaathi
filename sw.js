/*
  SafarSaathi AI Auto-Purge Service Worker (Version: v48-normal-sound-default)
  Zero Stale Cache • Network-First • Chrome & Safari Compatible
*/
const CACHE_NAME = 'safarsaathi-v48-normal-sound-default';

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

  // Always fetch fresh from network to prevent stale data
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});
