
const CACHE_NAME = 'chatbot-cache-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/chatbot.js',
  '/style.css',
];

// Installiere den Service Worker und cache wichtige Dateien
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Cache geöffnet');
        return cache.addAll(urlsToCache);
      })
  );
});

// Interceptiere Netzwerkanfragen und lade gecachte Daten
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Antwort aus dem Cache verwenden, falls vorhanden
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
