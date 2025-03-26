self.addEventListener('fetch', (event) => {
    const modifiedHeaders = new Headers(event.request.headers);
    modifiedHeaders.set('API-Key', '000000000000000000001');

    const newRequest = new Request(event.request, {
        headers: modifiedHeaders,
        mode: "cors"
    });

    console.log(newRequest.headers);

    event.respondWith((async () => fetch(newRequest))());
});
