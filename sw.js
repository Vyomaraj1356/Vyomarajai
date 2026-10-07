const CACHE_NAME = 'vyomaraj-public-shell-v1';
const BASE_URL = new URL('./', self.registration.scope);
const SHELL_URLS = [
  new URL('./', BASE_URL).href,
  new URL('./index.html', BASE_URL).href,
  new URL('./launch.css', BASE_URL).href,
  new URL('./launch.js', BASE_URL).href,
  new URL('./manifest.webmanifest', BASE_URL).href,
  new URL('./offline.html', BASE_URL).href,
  new URL('./assets/vyomaraj-icon.svg', BASE_URL).href,
  new URL('./assets/vyomaraj-icon-192.png', BASE_URL).href,
  new URL('./assets/vyomaraj-icon-512.png', BASE_URL).href
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_URLS)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key.startsWith('vyomaraj-public-shell-') && key !== CACHE_NAME)
        .map((key) => caches.delete(key))
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
  const requestUrl = new URL(request.url);
  if (!requestUrl.href.startsWith(BASE_URL.href)) return;

  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).catch(async () => {
      const cachedPage = await caches.match(new URL('./index.html', BASE_URL).href);
      return cachedPage || caches.match(new URL('./offline.html', BASE_URL).href);
    }));
    return;
  }

  if (SHELL_URLS.includes(requestUrl.href)) {
    event.respondWith(caches.match(request).then((cached) => cached || fetch(request)));
  }
});
