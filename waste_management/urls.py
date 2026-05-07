from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("core.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("collection/", include("collection.urls")),
    path("payments/", include("payments.urls")),
    path("complaints/", include("complaints.urls")),
    path("services/", include("services.urls")),
    path("recycling/", include("recycling.urls")),
    path("reports/", include("reports.urls")),
    path("tasks/", include("tasks.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
