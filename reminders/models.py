from django.conf import settings
from django.db import models
from core.models import BaseModel


class Reminder(BaseModel):
    class Channel(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        PUSH = "PUSH", "Push"

    class Meta:
        verbose_name = "Reminder"
        verbose_name_plural = "Reminders"
        db_table = "reminder"
        indexes = [
            models.Index(fields=["patient", "due_at"]),
            models.Index(fields=["active"]),
        ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reminders")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_reminders")  # doctor/admin or self
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, default="")
    due_at = models.DateTimeField()
    rrule = models.CharField(max_length=300, blank=True, default="")  # optional iCal RRULE for periodic check-ups
    preferred_channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.EMAIL)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
