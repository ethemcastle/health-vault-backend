from django.conf import settings
from django.db import models
from core.models import BaseModel


class Notification(BaseModel):
    class Kind(models.TextChoices):
        REMINDER = "REMINDER", "Reminder"
        SYSTEM = "SYSTEM", "System"
        ANALYSIS_READY = "ANALYSIS_READY", "Analysis ready"
        CONSENT = "CONSENT", "Consent"

    class Channel(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        PUSH = "PUSH", "Push"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        db_table = "notification"
        indexes = [
            models.Index(fields=["user", "date_created"]),
            models.Index(fields=["kind"]),
        ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices)
    subject = models.CharField(max_length=200)
    body = models.TextField(blank=True, default="")
    payload = models.JSONField(blank=True, default=dict)  # arbitrary context
    sent_at = models.DateTimeField(null=True, blank=True)
