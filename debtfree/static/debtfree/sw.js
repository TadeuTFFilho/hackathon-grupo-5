const CACHE_NAME = 'debtfree-v1';
const PRECACHE = [
  '/',
  '/login/',
  '/dashboard/',
  '/static/debtfree/manifest.json',
  '/static/debtfree/icon.svg',
  'https://cdn.tailwindcss.com',
];

// Instala e pré-cacheia recursos essenciais
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

// Remove caches antigos ao ativar
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Estratégia: Network first, fallback para cache
self.addEventListener('fetch', event => {
  // Ignora requisições não-GET e de outros origins
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith(self.location.origin) &&
      !event.request.url.startsWith('https://cdn.tailwindcss.com')) return;

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Atualiza o cache com a resposta mais recente
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
