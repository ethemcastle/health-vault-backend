from django.conf import settings
from django.db import models
from core.models import BaseModel


class AuditLog(BaseModel):
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        READ = "READ", "Read"
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        db_table = "audit_log"
        indexes = [
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["action", "date_created"]),
        ]
        ordering = ["-date_created"]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    target_type = models.CharField(max_length=120)   # e.g., "User", "Analysis"
    target_id = models.CharField(max_length=64)      # record ID as string
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(blank=True, default=dict)
