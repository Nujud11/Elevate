# project/urls.py
from django.urls import include, path, re_path
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from django.conf.urls.static import static
from search import views as search_views

from .api import api_router, api as ninja_api


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    path("accounts/", include("accounts.urls")),
    path("s/", include("students.urls")),
    path("c/", include("companies.urls")),
    path("search/", search_views.search, name="search"),

    # API URLs Pattern
    path("api/v2/", api_router.urls),   # Wagtail API

    path("api/ninja/", ninja_api.urls), # NINJA API

    re_path(r'^', include(wagtail_urls)),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
