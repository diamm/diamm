"""diamm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (
    password_reset, password_reset_done, password_reset_confirm, password_reset_complete,
    password_change, password_change_done, login, logout
)
from django_jinja import views as jinja_views

from diamm.views.auth import CreateAccount
from registration.backends.hmac.views import ActivationView
from diamm.views.user import ProfileView, ProfileEditView
from diamm.views.website.search import SearchView
from diamm.views.website.set import SetDetail
from diamm.views.website.source import (
    SourceDetail, SourceManifest, SourceCanvasDetail, legacy_item_redirect
)
from diamm.views.website.source import SourceRangeDetail, SourceItemDetail
from diamm.views.website.archive import ArchiveDetail
from diamm.views.website.city import CityList, CityDetail
from diamm.views.website.country import CountryDetail
from diamm.views.website.person import PersonDetail, legacy_composer_redirect
from diamm.views.website.organization import OrganizationDetail
from diamm.views.website.composition import CompositionDetail
from diamm.views.website.image import image_serve
from diamm.views.website.bibliography_author import BibliographyAuthorDetail
from diamm.views.website.commentary import CommentaryList
from diamm.views.catalogue.catalogue import CatalogueView
from diamm.views.website.correction import CorrectionCreate
from diamm.views.website.contributor import ContributorList

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from django.contrib.sitemaps import views as sitemap_views
from diamm.sitemaps.source_sitemap import SourceSitemap
from diamm.sitemaps.static_sitemap import StaticSitemap
from diamm.sitemaps.archive_sitemap import ArchiveSitemap

handler404 = jinja_views.PageNotFound.as_view()
handler403 = jinja_views.PermissionDenied.as_view()
handler400 = jinja_views.ErrorView.as_view()
handler500 = jinja_views.ServerError.as_view()


sitemaps = {
    "static": StaticSitemap(),
    "source": SourceSitemap(),
    "archive": ArchiveSitemap()
}

urlpatterns = [
    url(r'^search.xml$', TemplateView.as_view(template_name='opensearch.jinja2',
                                              content_type="application/opensearchdescription+xml"), name='opensearch'),
    url(r'^sitemap\.xml$', sitemap_views.index, {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.*)\.xml$', sitemap_views.sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type="text/plain"), name='robots-txt'),

    url(r'^admin/', admin.site.urls),
    url(r'^admin/salmonella/', include('salmonella.urls')),
    # url(r'^introduction/$', TemplateView.as_view(template_name="introduction.jinja2"), name="introduction"),
    # url(r'^technical/$', TemplateView.as_view(template_name="technical.jinja2"), name="technical"),

    # Authentication and account resets
    url(r'^login/$', login,
        {"template_name": 'website/auth/login.jinja2'}, name="login"),
    url(r'^logout/$', logout,
        {"next_page": "/"}, name="logout"),
    url(r'^register/$', CreateAccount.as_view(), name="register"),
    url(r'^reset/$', password_reset,
        {'template_name': 'website/auth/reset.jinja2',
         'from_email': settings.DEFAULT_FROM_EMAIL}, name="reset"),
    url(r'^reset/sent/$', password_reset_done,
        {"template_name": "website/auth/reset_sent.jinja2"}, name="password_reset_done"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm,
        {'post_reset_redirect': '/reset/complete/',
         'template_name': "website/auth/reset_confirm.jinja2"}, name="password_reset_confirm"),
    url(r'^reset/complete/$', password_reset_complete,
        {'template_name': "website/auth/reset_complete.jinja2"}),
    url(r'^change/$', password_change,
        {"template_name": 'website/auth/change.jinja2',
         "post_change_redirect": "/change/complete/"}, name="password-change"),
    url(r'^change/complete/$', password_change_done,
        {"template_name": "website/auth/change_complete.jinja2"},
        name="password-change-done"),
    url(r'activate/(?P<activation_key>[-:\w]+)/$',
            ActivationView.as_view(
                template_name="website/auth/activation.jinja2"
            ),
        name='registration_activate'),
    url(r'activate/complete/$', TemplateView.as_view(
        template_name="website/auth/activation.jinja2"
    ), name='registration_activation_complete'),


    url(r'^account/$', ProfileView.as_view(), name="user-account"),
    url(r'^account/edit/$', ProfileEditView.as_view(), name="user-account-edit"),

    # public website
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^sources/(?P<pk>[0-9]+)/$', SourceDetail.as_view(), name="source-detail"),
    url(r'^sources/(?P<pk>[0-9]+)/manifest/$', SourceManifest.as_view(), name="source-manifest"),

    # IIIF URIs. These do not necessarily always resolve, but are configured in the URLs so that they can reflect
    #  the host and protocol of the request.
    url(r'^sources/(?P<source_id>[0-9]+)/canvas/(?P<page_id>[0-9]+)/$', SourceCanvasDetail.as_view(), name="source-canvas-detail"),
    url(r'^sources/(?P<source_id>[0-9]+)/range/(?P<item_id>[0-9]+)/$', SourceRangeDetail.as_view(), name="source-range-detail"),
    url(r'^sources/(?P<source_id>[0-9]+)/item/(?P<item_id>[0-9]+)/$', SourceItemDetail.as_view(), name="source-item-detail"),
    url(r'^items/(?P<item_id>[0-9]+)/$', legacy_item_redirect),

    url(r'^archives/(?P<pk>[0-9]+)/$', ArchiveDetail.as_view(), name="archive-detail"),
    url(r'^cities/$', CityList.as_view(), name="city-list"),
    url(r'^cities/(?P<pk>[0-9]+)/$', CityDetail.as_view(), name="city-detail"),
    url(r'^countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name="country-detail"),

    # url(r'^people/$', PersonList.as_view(), name="person-list"),
    url(r'^people/(?P<pk>[0-9]+)/$', PersonDetail.as_view(), name="person-detail"),
    url(r'^organizations/(?P<pk>[0-9]+)/$', OrganizationDetail.as_view(), name="organization-detail"),
    url(r'^composers/(?P<legacy_id>[0-9]+)/$', legacy_composer_redirect),
    url(r'^compositions/(?P<pk>[0-9]+)/$', CompositionDetail.as_view(), name="composition-detail"),

    url(r'^sets/(?P<pk>[0-9]+)/$', SetDetail.as_view(), name="set-detail"),

    url(r'^authors/(?P<pk>[0-9]+)/$', BibliographyAuthorDetail.as_view(), name="author-detail"),

    url(r'^images/(?P<pk>[0-9]+)/(?:(?P<region>.*)/(?P<size>.*)/(?P<rotation>.*)/default\.jpg)$', image_serve, name="image-serve"),
    url(r'^images/(?P<pk>[0-9]+)/$', image_serve, name="image-serve-info"),

    url(r'^commentary/$', CommentaryList.as_view(), name="commentary-list"),

    # Two views on the same content; see the problem_report model for clarification.
    url(r'^corrections/$', CorrectionCreate.as_view(), name="correction-create"),
    url(r'^contributors/$', ContributorList.as_view(), name="contributor-list"),

    # Cataloguing view
    url(r'^catalogue/(.*)$', CatalogueView.as_view(), name="catalogue-view"),

    # Any routes that are not matched by the previous are routed to the Wagtail module
    #  which acts as a CMS for the non-database content.
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'', include(wagtail_urls)),
]
if settings.DEBUG:
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)

