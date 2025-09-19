from django.urls import path

from audit.model_views.audit_log_view import (
    AuditLogListView, AuditLogRetrieveView,
)

app_name = "audit"

urlpatterns = [
    path("", AuditLogListView.as_view(), name="auditlog-list"),
    path("<int:pk>/", AuditLogRetrieveView.as_view(), name="auditlog-retrieve"),
]
