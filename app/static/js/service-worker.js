// Nome do cache
const CACHE_NAME = 'gepes-classify-cache-v2';
const DATA_CACHE_NAME = 'gepes-classify-data-cache-v1';

// Arquivos para cache inicial (estáticos)
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/js/ai_suggestions.js',
  '/static/img/ai.png',
  '/static/img/dashboard.png',
  '/static/img/confianca.png',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  '/static/manifest.json',
  '/static/favicon.ico',
  '/login',
  '/projects',
  '/categories',
  '/lists',
  '/settings',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://code.jquery.com/jquery-3.6.0.min.js'
];

// Instalação do service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Ativação do service worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptação de requisições
self.addEventListener('fetch', event => {
  const requestUrl = new URL(event.request.url);
  
  // Estratégia diferente para requisições de dados vs. arquivos estáticos
  if (requestUrl.pathname.includes('/data/') || requestUrl.pathname.includes('/api/')) {
    // Estratégia Cache then Network para dados
    event.respondWith(
      caches.open(DATA_CACHE_NAME).then(cache => {
        return fetch(event.request)
          .then(response => {
            // Se a resposta for válida, armazena no cache
            if (response.status === 200) {
              cache.put(event.request, response.clone());
            }
            return response;
          })
          .catch(() => {
            // Se falhar, tenta buscar do cache
            return cache.match(event.request);
          });
      })
    );
  } else {
    // Estratégia Cache First para recursos estáticos
    event.respondWith(
      caches.match(event.request).then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        return fetch(event.request).then(response => {
          // Verifica se a resposta é válida
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone da resposta
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
          
          return response;
        }).catch(() => {
          // Retorna uma página offline se disponível
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
          
          return new Response('Offline', {
            status: 503,
            statusText: 'Service Unavailable'
          });
        });
      })
    );
  }
});

// Evento para lidar com mensagens (útil para forçar atualização)
self.addEventListener('message', event => {
  if (event.data.action === 'skipWaiting') {
    self.skipWaiting();
  }
});
