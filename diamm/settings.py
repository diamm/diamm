"""
Django settings for diamm project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from diamm.settings_local import *
from django_jinja.builtins import DEFAULT_EXTENSIONS

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@l%t#fyhaahycu$gct^u5ttya69v5n^00y48@)2mngdlel63g+'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '*'
]
INTERNAL_IPS = (
    '127.0.0.1'
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'diamm',
    'diamm.diamm_data',
    'diamm.diamm_migrate',
    'diamm.diamm_site',
    'reversion',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'django_jinja',
    'pagedown',
    'debug_toolbar'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'diamm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        "OPTIONS": {
            'trim_blocks': True,
            'autoescape': True,
            'lstrip_blocks': True,
            'match_extension': '.jinja2',
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ]
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'diamm.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'diamm_data_server',
        'HOST': 'localhost',
        'PORT': '5432',
        'USER': 'diamm_data',
        'PASSWORD': 'diamm123'
    },
    'migrate': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'diamm_data_migration',
        'HOST': 'localhost',
        'PORT': '5432',
        'USER': 'diamm_data',
        'PASSWORD': 'diamm123'
    }
}
DATABASE_ROUTERS = ['diamm.router.LegacyRouter']

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'diamm_cache_table',
#     }
# }

JINJA2_ENVIRONMENT_OPTIONS = {
    'trim_blocks': True,
    'autoescape': True,
    'lstrip_blocks': True
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'diamm.renderers.html_renderer.HTMLRenderer',
        'drf_ujson.renderers.UJSONRenderer',
    ),
}

SOLR = {
    'SERVER': "http://localhost:8983/solr/diamm/",
    'PAGE_SIZE': REST_FRAMEWORK['PAGE_SIZE'],
    'DEFAULT_OPERATOR': 'AND',
    'INDEX_TYPES': {
        'SOURCE': {
            'type': 'source',
            'name': 'Source',
            'view': 'source-detail'
        }
    },
    'SEARCH_TYPES': [  # These are the solr types that will be returned in a full-text search.
        'archive',
        'source',
        'person',
        'organization',
        'set',
        'composition'
    ],
    'FACET_FIELDS': [
        '{!ex=type}type',
        '{!ex=type}public_images_b'
    ],
    'FULLTEXT_QUERYFIELDS': [    # Boosting these fields allows more common methods of referring to a MSS to bubble up in the search results.
        'text',
        'source_boost_tns^10',  # Boost specific fields for source records that may be used at query time.
        'archive_boost_tns^5'
    ]
}

IIIF = {
    "THUMBNAIL_WIDTH": "250,"   # The constrained width of thumbnail images
}

if DEBUG:
    SILENCED_SYSTEM_CHECKS = []
