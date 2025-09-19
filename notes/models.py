from django.conf import settings
from django.db import models
from core.models import BaseModel


def clinical_attachment_path(instance: "ClinicalNoteAttachment", filename: str) -> str:
    return f"notes/{instance.note.patient_id}/{instance.note_id}/{filename}"


class ClinicalNote(BaseModel):
    class Meta:
        verbose_name = "Clinical Note"
        verbose_name_plural = "Clinical Notes"
        db_table = "clinical_note"
        indexes = [
            models.Index(fields=["patient", "date_created"]),
        ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clinical_notes")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="authored_notes")
    title = models.CharField(max_length=160)
    body = models.TextField()


class ClinicalNoteAttachment(BaseModel):
    class Meta:
        verbose_name = "Clinical Note Attachment"
        verbose_name_plural = "Clinical Note Attachments"
        db_table = "clinical_note_attachment"

    note = models.ForeignKey(ClinicalNote, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=clinical_attachment_path)
