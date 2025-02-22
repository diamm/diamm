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

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.contrib.sitemaps import views as sitemap_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http.response import HttpResponseRedirectBase
from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from django_jinja import views as jinja_views
from django_registration.backends.activation.views import ActivationView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from diamm.sitemaps.archive_sitemap import ArchiveSitemap
from diamm.sitemaps.source_sitemap import SourceSitemap
from diamm.sitemaps.static_sitemap import StaticSitemap
from diamm.views.auth import CreateAccount
from diamm.views.user import ProfileEditView, ProfileView
from diamm.views.website.archive import ArchiveDetail
from diamm.views.website.bibliography_author import BibliographyAuthorDetail
from diamm.views.website.city import CityDetail, CityList
from diamm.views.website.commentary import commentary_submit
from diamm.views.website.composition import CompositionDetail
from diamm.views.website.correction import correction_submit
from diamm.views.website.country import CountryDetail, CountryList
from diamm.views.website.image import (
    cover_image_serve,
    image_serve,
    image_serve_redirect,
)
from diamm.views.website.organization import OrganizationDetail
from diamm.views.website.person import PersonDetail, legacy_composer_redirect
from diamm.views.website.region import RegionDetail
from diamm.views.website.search import SearchView
from diamm.views.website.set import SetDetail
from diamm.views.website.source import (
    SourceCanvasDetail,
    SourceDetail,
    SourceItemDetail,
    SourceManifest,
    SourceRangeDetail,
    legacy_item_redirect,
)

handler404 = jinja_views.PageNotFound.as_view()
handler403 = jinja_views.PermissionDenied.as_view()
handler400 = jinja_views.ErrorView.as_view()
# handler500 = jinja_views.ServerError.as_view()


def redirect_303(request, new_url):
    return HttpResponseRedirectBase(new_url, status=303, request=request)


sitemaps = {
    "static": StaticSitemap(),
    "source": SourceSitemap(),
    "archive": ArchiveSitemap(),
}

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url("favicon.ico"), permanent=False
        ),
        name="favicon",
    ),
    path(
        "search.xml",
        TemplateView.as_view(
            template_name="opensearch.jinja2",
            content_type="application/opensearchdescription+xml",
        ),
        name="opensearch",
    ),
    path("sitemap.xml", sitemap_views.index, {"sitemaps": sitemaps}),
    path(
        "sitemap-<str:section>.xml",
        sitemap_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots-txt",
    ),
    path("admin/", admin.site.urls),
    # url(r'^introduction/$', TemplateView.as_view(template_name="introduction.jinja2"), name="introduction"),
    # url(r'^technical/$', TemplateView.as_view(template_name="technical.jinja2"), name="technical"),
    # Authentication and account resets
    path(
        "login/",
        LoginView.as_view(template_name="website/auth/login.jinja2"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", CreateAccount.as_view(), name="register"),
    path(
        "reset/",
        PasswordResetView.as_view(
            template_name="website/auth/reset.jinja2",
            from_email=settings.DEFAULT_FROM_EMAIL,
        ),
        name="reset",
    ),
    path(
        "reset/sent/",
        PasswordResetDoneView.as_view(template_name="website/auth/reset_sent.jinja2"),
        name="password_reset_done",
    ),
    re_path(
        r"^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/",
        PasswordResetConfirmView.as_view(
            template_name="website/auth/reset_confirm.jinja2",
            success_url="/reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="website/auth/reset_complete.jinja2"
        ),
    ),
    path(
        "change/",
        PasswordChangeView.as_view(
            template_name="website/auth/change.jinja2", success_url="/change/complete/"
        ),
        name="password-change",
    ),
    path(
        "change/complete/",
        PasswordChangeDoneView.as_view(
            template_name="website/auth/change_complete.jinja2"
        ),
        name="password-change-done",
    ),
    re_path(
        r"activate/$",
        ActivationView.as_view(template_name="website/auth/activation_form.jinja2"),
        name="registration_activate",
    ),
    path(
        "activate/complete/",
        TemplateView.as_view(template_name="website/auth/activation.jinja2"),
        name="django_registration_activation_complete",
    ),
    path("account/", ProfileView.as_view(), name="user-account"),
    path("account/edit/", ProfileEditView.as_view(), name="user-account-edit"),
    # public website
    path("search/", SearchView.as_view(), name="search"),
    path("sources/<int:pk>/", SourceDetail.as_view(), name="source-detail"),
    path(
        "sources/<int:pk>/manifest/", SourceManifest.as_view(), name="source-manifest"
    ),
    # IIIF URIs. These do not necessarily always resolve, but are configured in the URLs so that they can reflect
    #  the host and protocol of the request.
    path(
        "sources/<int:source_id>/canvas/<int:page_id>/",
        SourceCanvasDetail.as_view(),
        name="source-canvas-detail",
    ),
    path(
        "sources/<int:source_id>/range/<int:item_id>/",
        SourceRangeDetail.as_view(),
        name="source-range-detail",
    ),
    path(
        "sources/<int:source_id>/item/<int:item_id>/",
        SourceItemDetail.as_view(),
        name="source-item-detail",
    ),
    path("items/<int:item_id>/", legacy_item_redirect),
    path("archives/<int:pk>/", ArchiveDetail.as_view(), name="archive-detail"),
    path("cities/", CityList.as_view(), name="city-list"),
    path("cities/<int:pk>/", CityDetail.as_view(), name="city-detail"),
    path("countries/<int:pk>/", CountryDetail.as_view(), name="country-detail"),
    path("countries/", CountryList.as_view(), name="country-list"),
    path("regions/<int:pk>/", RegionDetail.as_view(), name="region-detail"),
    # url(r'^people/$', PersonList.as_view(), name="person-list"),
    path("people/<int:pk>/", PersonDetail.as_view(), name="person-detail"),
    path(
        "organizations/<int:pk>/",
        OrganizationDetail.as_view(),
        name="organization-detail",
    ),
    path("composers/<int:pk>/", legacy_composer_redirect),
    path(
        "compositions/<int:pk>/", CompositionDetail.as_view(), name="composition-detail"
    ),
    path("sets/<int:pk>/", SetDetail.as_view(), name="set-detail"),
    path("authors/<int:pk>/", BibliographyAuthorDetail.as_view(), name="author-detail"),
    re_path(
        r"^images/(?P<pk>[0-9]+)/(?P<region>(?:pct:)?[0-9,]+|full|square)/(?P<size>.*)/(?P<rotation>.*)/default\.jpg$",
        image_serve,
        name="image-serve",
    ),
    path("images/<int:pk>/", image_serve_redirect, name="image-serve-redirect"),
    path("images/<int:pk>/info.json", image_serve, name="image-serve-info"),
    path("cover/<int:pk>/", cover_image_serve, name="cover-image"),
    path("commentary/", commentary_submit, name="commentary-submit"),
    # Two views on the same content; see the problem_report model for clarification.
    path("corrections/", correction_submit, name="correction-create"),
    # Cataloguing view
    # url(r'^catalogue/(.*)$', CatalogueView.as_view(), name="catalogue-view"),
    # Any routes that are not matched by the previous are routed to the Wagtail module
    #  which acts as a CMS for the non-database content.
    path("__debug__/", include("debug_toolbar.urls")),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("", include(wagtail_urls)),
]
if settings.DEBUG:
    urlpatterns += static("/static/", document_root=settings.STATIC_ROOT)
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
