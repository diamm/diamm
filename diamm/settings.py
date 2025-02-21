"""
Django settings for diamm project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

from django_jinja.builtins import DEFAULT_EXTENSIONS

from diamm.settings_local import *  # noqa: F403

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

CSRF_TRUSTED_ORIGINS = ["https://www.diamm.ac.uk"]
ALLOWED_HOSTS = ["www.diamm.ac.uk"]

if DEBUG:  # noqa: F405
    CSRF_TRUSTED_ORIGINS.append("http://dev.diamm.ac.uk")
    ALLOWED_HOSTS.append("dev.diamm.ac.uk")

INTERNAL_IPS = "127.0.0.1"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "diamm",
    "diamm.diamm_data",
    "diamm.diamm_site",
    "reversion",
    "rest_framework",
    "django_extensions",
    "django_jinja",
    "django_jinja.contrib._humanize",
    "pagedown",
    # wagtail config for CMS
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.contrib.sitemaps",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # 'django.middleware.cache.UpdateCacheMiddleware',
    "django.middleware.common.CommonMiddleware",
    #'django.middleware.cache.FetchFromCacheMiddleware',
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    # 'wagtail.wagtailcore.middleware.SiteMiddleware',
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

if DEBUG:  # noqa: F405
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.append(
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )


ROOT_URLCONF = "diamm.urls"

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "APP_DIRS": True,
        "OPTIONS": {
            "trim_blocks": True,
            "autoescape": True,
            "lstrip_blocks": True,
            "match_extension": ".jinja2",
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "extensions": DEFAULT_EXTENSIONS
            + [
                "wagtail.jinja2tags.core",
                "wagtail.admin.jinja2tags.userbar",
                "wagtail.images.jinja2tags.images",
                "django_jinja.builtins.extensions.DjangoFiltersExtension",
            ],
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    },
]

WSGI_APPLICATION = "diamm.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

# DATABASE_ROUTERS = ['diamm.router.DatabaseRouter']

# Some records fail with too many fields if this check is not disabled.
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_USER_MODEL = "diamm_site.CustomUserModel"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/account/"
ACCOUNT_ACTIVATION_DAYS = 7

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = "/static/"

# CACHES = {
#     'default': {
#         'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
#         'LOCATION': 'localhost:11211',
#         'TIMEOUT': 500,
#         'BINARY': True,
#         'OPTIONS': {  # Maps to pylibmc "behaviors"
#             'tcp_nodelay': True,
#             'ketama': True
#         }
#     }
# }

DEFAULT_JINJA2_TEMPLATE_EXTENSION = ".jinja2"
JINJA2_ENVIRONMENT_OPTIONS = {
    "trim_blocks": True,
    "autoescape": True,
    "lstrip_blocks": True,
}

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": (
        "diamm.renderers.html_renderer.HTMLRenderer",
        "diamm.renderers.ujson_renderer.UJSONRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "diamm.authentication.DiammTokenAuthentication",
    ),
}

# These fields are exposed as facets to the front-end. Note that their
# presence here is a prerequisite to there being a facet block in the
# React search application.
INTERFACE_FACETS = {
    "cities": "facet_cities_ss",
    "genres": "genres_ss",
    "notations": "notations_ss",
    "composers": "composers_ss",
    "archive_locations": ["country_s", "city_s"],  # an array creates a pivot facet
    "source_type": "source_type_s",
    "has_inventory": "inventory_provided_b",
    "organization_type": "organization_type_s",
    "location": "location_s",
    "archive": "archive_s",
    "anonymous": "anonymous_b",
    # "source_date_range": "facet_date_range_ii"
}

SOLR = {
    "SERVER": "http://localhost:8983/solr/diamm/",
    "INDEX_SERVER": "http://localhost:8983/solr/diamm_ingest/",  # Indexing core. This is then swapped for the live one.
    "BASE_SERVER": "http://localhost:8983/solr",
    "INDEX_CORE": "diamm_ingest",
    "LIVE_CORE": "diamm",
    "PAGE_SIZE": REST_FRAMEWORK[
        "PAGE_SIZE"
    ],  # use the same page size as DRF for consistency
    "DEFAULT_OPERATOR": "AND",
    "INDEX_TYPES": {
        "SOURCE": {"type": "source", "name": "Source", "view": "source-detail"}
    },
    "SEARCH_TYPES": [  # These are the solr types that will be returned in a full-text search.
        "archive",
        "source",
        "person",
        "organization",
        "set",
        "composition",
    ],
    "FACET_FIELDS": [  # Use the interface facets to define public-facing facet fields.
        "{!ex=type}type",
        "{!ex=type}public_images_b",
    ],
    "FACET_PIVOTS": [],
    "FACET_SORT": {  # custom sorting for certain facets (default is by count; index is alphanumeric)
        "f.composers_ss.facet.sort": "index",
        "f.country_s.facet.sort": "index",
        "f.city_s.facet.sort": "index",
        "f.name_s.facet.sort": "index",
        "f.genres_ss.facet.sort": "index",
        "f.archive_s.facet.sort": "index",
    },
    "FULLTEXT_QUERYFIELDS": [  # Boosting these fields allows more common methods of referring to a MSS to bubble up in the search results.
        "text",
        "source_boost_tns^10",  # Boost specific fields for source records that may be used at query time.
        "archive_boost_tns^5",
    ],
    "TYPE_SORTS": {
        "archive": "name_ans asc",
        "set": "cluster_shelfmark_ans asc",
        "person": "name_ans asc",
        "organization": "name_ans asc",
        "composition": "title_ans asc",
        "source": "display_name_s asc, archive_city_s asc",
        "sources_with_images": "display_name_s asc, archive_city_s asc",
    },
}

# do some manipulation to get the interface facets into the Solr configuration
# We assign the solr output key to the key of the interface facet dict for
# consistent reference, and so we can more easily work with it in the search response
# handler.
for k, v in INTERFACE_FACETS.items():
    if isinstance(v, list):
        pfacet = f"{{!key={k}}}{','.join(v)}"
        SOLR["FACET_PIVOTS"].append(pfacet)
    else:
        facet = f"{{!key={k}}}{v}"
        SOLR["FACET_FIELDS"].append(facet)

IIIF = {
    "THUMBNAIL_WIDTH": "250,"  # The constrained width of thumbnail images
}

MAIL = {
    "CONFIRMATION_MESSAGE": """
Dear {first_name} {last_name},

Please confirm your new account on {hostname} by clicking on the following link:

{confirmation_link}

Note that this link will expire after 24 hours and you will need to have a new confirmation e-mail sent to you.

---
The Digital Image Archive of Medieval Music
https://www.diamm.ac.uk
diamm@music.ox.ac.uk
    """,
    "CORRECTION_THANK_YOU": """

Dear {name},

Thank you for submitting a correction to "{record}". We will review your submission and contact you if any further information is needed.

Should your correction be accepted, your name will be credited under the "Contributors" section for this record. You can view your contributions, both active and pending, on your user profile page.

---
The Digital Image Archive of Medieval Music
https://www.diamm.ac.uk
diamm@music.ox.ac.uk
    """,
    "CORRECTION_ADMIN": """
Dear colleague,

A new correction report for "{record}" has been submitted by {name}:

---
{report}
---
This report is available for review at {review_url}.

The record to be corrected is at {record_url}.

---
The Digital Image Archive of Medieval Music
https://www.diamm.ac.uk
diamm@music.ox.ac.uk

    """,
    "ISSUE_RESOLVED": """
Dear {name},

The issue with "{record}" you reported has been marked as fixed. A summary of your contribution will appear on the record as follows:

{summary}

Thank you for your contribution.

---
Your original report:

{original_report}

---
The Digital Image Archive of Medieval Music
https://www.diamm.ac.uk
diamm@music.ox.ac.uk
""",
}

WAGTAIL_SITE_NAME = "Digital Image Archive of Medieval Music"
WAGTAILADMIN_BASE_URL = f"{HOSTNAME}"  # noqa: F405

if DEBUG:  # noqa: F405
    MIDDLEWARE = ["diamm.middleware.logging.QueryCountDebugMiddleware"] + MIDDLEWARE
    SILENCED_SYSTEM_CHECKS = []

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] [%(levelname)8s] (%(name)s) %(message)s (%(filename)s:%(lineno)s)",
            "style": "%",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "diamm": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        # "django.db.backends": {
        #     "level": "DEBUG",
        #     "handlers": ["console"],
        # },
        "diamm.middleware.logging": {"handlers": ["console"], "level": "DEBUG"},
    },
}
