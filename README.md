# The Digital Image Archive of Medieval Music

This project is the website of the [Digital Image Archive of Medieval Music](https://www.diamm.ac.uk). While just having the source code is likely not directly useful to others, publishing the code behind the website as open source is one component of our efforts to sustain this project in the long term.

Our [Issues](https://github.com/diamm/diamm/issues) page tracks all known problems and feature requests for the site, along with any discussions around that issue. When an issue has been resolved it is 'closed,' but still available for review. Issues that require changes to the code of the site will usually be linked together, so a person reporting the issue can be apprised of changes arising from their report. See [this report](https://github.com/diamm/diamm/issues/188) for an example.

Our development process has all 'in-progress' code committed to the 'develop' branch. New releases of the code mean these developments are merged to the 'master' branch, and a new release tag created. The version of the site on the master branch is always the version that is running the live site. A list of all changes to the site can be found by [reviewing our commits](https://github.com/diamm/diamm/commits/master).

## Components and Technologies

The site is built using the Django web framework. It uses a PostgreSQL database and an instance of the Solr search engine for its data storage and search capabilities.

The [Django REST Framework](http://www.django-rest-framework.org) forms a crucial part of the site's functionality. It provides a machine-readable representation for every entity in the database, content negotiation capabilities, and HTTP method-based security.

The site is served with the NginX web server and the gunicorn FastCGI application server. The images are served using the [IIP Image Server](http://iipimage.sourceforge.net/documentation/server/). 

All of our images are available as [IIIF Image API](http://iiif.io/api/image/2.1/) endpoints, and we deliver [IIIF Presentation API](http://iiif.io/api/presentation/2.1/) manifests for every source with images. The only caveat is that you must be authenticated with a username and password to access these, due to licensing restrictions with our partner libraries.

## Protected IIIF Images

Image delivery is handled by Nginx. Django no longer streams image bytes in supported environments.

- Canonical protected IIIF URLs stay under `/images/<pk>/info.json` and `/images/<pk>/<region>/<size>/<rotation>/default.jpg`.
- Canonical public cover URLs stay under `/cover/<pk>/`.
- Nginx should also own the `303` redirect from `/images/<pk>/` to `/images/<pk>/info.json`.
- Diva tile requests do not send `Authorization` headers, so protected image access depends on the normal same-origin Django session cookie.
- Nginx sends protected requests to `/auth/images/` with `Cookie` and `X-Original-URI`.
- Django authenticates the session user, resolves `Image.location` from cache backed by the `Image` model, and returns `204 No Content` plus `X-DIAMM-Backend-URI`.
- Nginx proxies that backend URI to the remote IIIF server with the required SNI, `Host`, `Referer`, and `X-DIAMM` headers.
- If the upstream rejects `http://dev...` or other non-canonical referers, use a fixed allowed HTTPS referer such as `https://www.diamm.ac.uk/` instead of `$scheme://$host`.
- Public `/cover/<pk>/` uses the same backend-resolution pattern, but without authentication, and always resolves to the fixed low-resolution backend shape `/full/400,/0/default.jpg`.

Direct requests that reach Django on `/images/...` or `/cover/...` return `501 Not Implemented`; that indicates Nginx is not configured in front of the application.

Working Nginx shape:

```nginx
location ~ ^/images/(?<pk>\d+)/$ {
    return 303 /images/$pk/info.json;
}

location /images/ {
    auth_request /auth/images/;
    auth_request_set $diamm_backend_uri $upstream_http_x_diamm_backend_uri;

    proxy_pass $diamm_backend_uri;
    proxy_ssl_server_name on;
    proxy_ssl_name www.diamm.ac.uk;
    proxy_set_header Host www.diamm.ac.uk;
    proxy_set_header Referer https://www.diamm.ac.uk/;
    proxy_set_header X-DIAMM your-diamm-image-key;
    proxy_buffering on;
}

location = /auth/images/ {
    internal;
    proxy_pass http://diamm/auth/images/;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header Host $host;
    proxy_set_header Cookie $http_cookie;
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /cover/ {
    # Public cover images still need an internal lookup so Django can resolve
    # <pk> to a fixed-size IIIF backend URL; this is not user authentication.
    auth_request /auth/covers/;
    auth_request_set $diamm_backend_uri $upstream_http_x_diamm_backend_uri;

    proxy_pass $diamm_backend_uri;
    proxy_ssl_server_name on;
    proxy_ssl_name www.diamm.ac.uk;
    proxy_set_header Host www.diamm.ac.uk;
    proxy_set_header Referer https://www.diamm.ac.uk/;
    proxy_set_header X-DIAMM your-diamm-image-key;
    proxy_buffering on;
}

location = /auth/covers/ {
    internal;
    proxy_pass http://diamm/auth/covers/;
    proxy_pass_request_body off;
    proxy_set_header Content-Length "";
    proxy_set_header Host $host;
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
