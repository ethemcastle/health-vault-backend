from rest_framework import serializers
from notifications.models import Notification


class NotificationReadSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "user", "user_email",
            "kind", "channel",
            "subject", "body",
            "payload",
            "sent_at",
            "date_created", "date_last_updated",
        ]
        read_only_fields = ["id", "user_email", "date_created", "date_last_updated"]


class NotificationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "kind", "channel",
            "subject", "body",
            "payload",
            "sent_at",
        ]
        read_only_fields = ["id"]
