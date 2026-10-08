// Cache only the public app shell. Never cache APIs, observations or credentials.
const CACHE = "troubleshoot-shell-v2";
const SHELL = ["/", "/app.js", "/style.css", "/manifest.webmanifest", "/icon-192.png", "/icon-512.png", "/fonts/space-grotesk.woff2", "/fonts/dm-mono.woff2"];
self.addEventListener("install", event => event.waitUntil(
  caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting())
));
self.addEventListener("activate", event => event.waitUntil(
  caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith("troubleshoot-shell-") && key !== CACHE).map(key => caches.delete(key))))
    .then(() => self.clients.claim())
));
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin || !SHELL.includes(url.pathname) || url.search) return;
  event.respondWith(fetch(event.request).catch(() => caches.open(CACHE).then(cache => cache.match(url.pathname))));
});
