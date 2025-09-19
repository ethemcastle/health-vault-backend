from rest_framework import serializers
from audit.models import AuditLog


class AuditLogReadSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor", "actor_email",
            "action",
            "target_type", "target_id",
            "ip_address", "metadata",
            "date_created", "date_last_updated",
        ]
        read_only_fields = ["id", "actor_email", "date_created", "date_last_updated"]
