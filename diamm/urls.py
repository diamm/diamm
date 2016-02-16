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
from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib import admin

from diamm.views.home import HomeView
from diamm.views.auth import SessionAuth, SessionClose, AccountEmailSent, AccountUpdate
from diamm.views.user import ProfileView
from diamm.views.website.search import SearchView
from diamm.views.website.source import SourceList, SourceDetail, SourceManifest
from diamm.views.website.archive import ArchiveList, ArchiveDetail
from diamm.views.website.city import CityList, CityDetail
from diamm.views.website.country import CountryList, CountryDetail
from diamm.views.website.person import PersonList, PersonDetail, legacy_composer_redirect
from diamm.views.website.organization import OrganizationList, OrganizationDetail
from diamm.views.website.composition import CompositionList, CompositionDetail
from diamm.views.website.story import StoryDetail


urlpatterns = [
    url(r'^search.xml$', TemplateView.as_view(template_name='opensearch.jinja2', content_type="application/opensearchdescription+xml"), name='opensearch'),
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^login/$', SessionAuth.as_view(), name="login"),
    url(r'^logout/$', SessionClose.as_view(), name="logout"),
    url(r'^login/update/$', AccountUpdate.as_view(), name="account-update"),
    url(r'^login/email-sent/$', AccountEmailSent.as_view(), name="account-email"),
    url(r'^user/(?P<pk>[0-9]+)/$', ProfileView.as_view(), name="user-profile"),

    # public website
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^news/(?P<pk>[0-9]+)/$', StoryDetail.as_view(), name="story-detail"),

    url(r'^sources/$', SourceList.as_view(), name="source-list"),
    url(r'^sources/(?P<pk>[0-9]+)/$', SourceDetail.as_view(), name="source-detail"),
    url(r'^sources/(?P<pk>[0-9]+)/manifest/$', SourceManifest.as_view(), name="source-manifest"),


    url(r'^archives/$', ArchiveList.as_view(), name="archive-list"),
    url(r'^archives/(?P<pk>[0-9]+)/$', ArchiveDetail.as_view(), name="archive-detail"),
    url(r'^cities/$', CityList.as_view(), name="city-list"),
    url(r'^cities/(?P<pk>[0-9]+)/$', CityDetail.as_view(), name="city-detail"),
    url(r'^countries/$', CountryList.as_view(), name="country-list"),
    url(r'^countries/(?P<pk>[0-9]+)/$', CountryDetail.as_view(), name="country-detail"),
    url(r'^people/$', PersonList.as_view(), name="person-list"),
    url(r'^people/(?P<pk>[0-9]+)/$', PersonDetail.as_view(), name="person-detail"),
    url(r'^organizations/$', OrganizationList.as_view(), name='organization-list'),
    url(r'^organizations/(?P<pk>[0-9]+)/$', OrganizationDetail.as_view(), name="organization-detail"),
    url(r'^composers/(?P<legacy_id>[0-9]+)/$', legacy_composer_redirect),
    url(r'^compositions/$', CompositionList.as_view(), name="composition-list"),
    url(r'^compositions/(?P<pk>[0-9]+)/$', CompositionDetail.as_view(), name="composition-detail"),
]

