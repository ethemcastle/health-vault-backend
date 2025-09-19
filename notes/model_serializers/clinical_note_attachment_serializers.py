from rest_framework import serializers
from notes.models import ClinicalNoteAttachment


class ClinicalNoteAttachmentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNoteAttachment
        fields = ["id", "note", "file", "date_created", "date_last_updated"]
        read_only_fields = ["id", "date_created", "date_last_updated"]


class ClinicalNoteAttachmentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNoteAttachment
        fields = ["id", "note", "file"]
        read_only_fields = ["id"]
