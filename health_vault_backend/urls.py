from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
   openapi.Info(
      title="My Django API",
      default_version='v1',
      description="API documentation for my Django app",
      contact=openapi.Contact(email="support@example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("authentication/", include("authentication.urls", namespace="authentication")),
    path("profiles/", include("profiles.urls", namespace="profiles")),
    path("analyses/", include("analyses.urls", namespace="analyses")),
    path("notes/", include("notes.urls", namespace="notes")),
    path("reminders/", include("reminders.urls", namespace="reminders")),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("auditlog/", include("audit.urls", namespace="audit")),

    path("api/schema/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/schema/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/schema.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
