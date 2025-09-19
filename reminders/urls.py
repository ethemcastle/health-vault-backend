from django.urls import path

from reminders.model_views.reminder_view import (
    ReminderListCreateView, ReminderRUDView,
)

app_name = "reminders"

urlpatterns = [
    path("", ReminderListCreateView.as_view(), name="reminder-list-create"),
    path("<int:pk>/", ReminderRUDView.as_view(), name="reminder-rud"),
]
