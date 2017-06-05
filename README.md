# The Digital Image Archive of Medieval Music

This project is the website of the [Digital Image Archive of Medieval Music](https://www.diamm.ac.uk). While just having the source code is likely not directly useful to others, publishing the code behind the website as open source is one component of our efforts to sustain this project in the long term.

Our [Issues](https://github.com/diamm/diamm/issues) page tracks all known problems and feature requests for the site, along with any discussions around that issue. When an issue has been resolved it is 'closed,' but still available for review. Issues that require changes to the code of the site will usually be linked together, so a person reporting the issue can be apprised of changes arising from their report. See [this report](https://github.com/diamm/diamm/issues/188) for an example.

Our development process has all 'in-progress' code committed to the 'develop' branch. New releases of the code mean these developments are merged to the 'master' branch, and a new release tag created. The version of the site on the master branch is always the version that is running the live site. A list of all changes to the site can be found by [reviewing our commits](https://github.com/diamm/diamm/commits/master).

## Components and Technologies

The site is built using the Django web framework. It uses a PostgreSQL database and an instance of the Solr search engine for its data storage and search capabilities. The front-end for the 'Source' view and the 'Search' view are built using ReactJS with Redux. (Other page views are rendered using Jinja2 templates.)

The [Django REST Framework](http://www.django-rest-framework.org) forms a crucial part of the site's functionality. It provides a machine-readable representation for every entity in the database, content negotiation capabilities, and HTTP method-based security.

The site is served with the NginX web server and the gunicorn FastCGI application server. The images are served using the [IIP Image Server](http://iipimage.sourceforge.net/documentation/server/). 

All of our images are available as [IIIF Image API](http://iiif.io/api/image/2.1/) endpoints, and we deliver [IIIF Presentation API](http://iiif.io/api/presentation/2.1/) manifests for every source with images. The only caveat is that you must be authenticated with a username and password to access these, due to licensing restrictions with our partner libraries.
