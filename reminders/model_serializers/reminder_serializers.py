from rest_framework import serializers
from reminders.models import Reminder


class ReminderReadSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Reminder
        fields = [
            "id",
            "patient", "patient_email",
            "created_by", "created_by_email",
            "title", "description",
            "due_at", "rrule", "preferred_channel",
            "last_sent_at", "active",
            "date_created", "date_last_updated",
        ]
        read_only_fields = ["id", "patient_email", "created_by_email", "date_created", "date_last_updated"]


class ReminderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = [
            "id",
            "patient",
            "created_by",
            "title",
            "description",
            "due_at",
            "rrule",
            "preferred_channel",
            "active",
        ]
        read_only_fields = ["id"]
