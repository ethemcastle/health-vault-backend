from rest_framework import serializers
from notes.models import ClinicalNote
from .clinical_note_attachment_serializers import ClinicalNoteAttachmentReadSerializer


class ClinicalNoteReadSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    doctor_email = serializers.EmailField(source="doctor.email", read_only=True)
    attachments = ClinicalNoteAttachmentReadSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicalNote
        fields = [
            "id",
            "patient", "patient_email",
            "doctor", "doctor_email",
            "title", "body",
            "attachments",
            "date_created", "date_last_updated",
        ]
        read_only_fields = ["id", "patient_email", "doctor_email", "attachments", "date_created", "date_last_updated"]


class ClinicalNoteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNote
        fields = ["id", "patient", "doctor", "title", "body"]
        read_only_fields = ["id"]
