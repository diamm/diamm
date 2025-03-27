self.addEventListener('fetch', (event) => {
    if (event.request.destination !== "image")
    {
        return;
    }
    const searchParams = new URL(location).searchParams;
    const apiKey = searchParams.get('key');
    const apiSecret = searchParams.get('secret');
    const apiDomain = searchParams.get('domain');

    const modifiedHeaders = new Headers(event.request.headers);
    modifiedHeaders.set('API-Key', '000000000000000000001');

    const newRequest = new Request(event.request, {
        headers: modifiedHeaders,
        mode: "cors"
    });

    event.respondWith((async () => fetch(newRequest))());
});
