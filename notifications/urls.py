from django.urls import path

from notifications.model_views.notification_view import (
    NotificationListCreateView, NotificationRUDView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationListCreateView.as_view(), name="notification-list-create"),
    path("<int:pk>/", NotificationRUDView.as_view(), name="notification-rud"),
]
