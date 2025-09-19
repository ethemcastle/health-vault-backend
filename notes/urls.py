from django.urls import path

from notes.model_views.clinical_note_view import (
    ClinicalNoteListCreateView, ClinicalNoteRUDView,
)
from notes.model_views.clinical_note_attachment_view import (
    ClinicalNoteAttachmentListCreateView, ClinicalNoteAttachmentRUDView,
)

app_name = "notes"

urlpatterns = [
    # Clinical notes
    path("", ClinicalNoteListCreateView.as_view(), name="clinicalnote-list-create"),
    path("<int:pk>/", ClinicalNoteRUDView.as_view(), name="clinicalnote-rud"),

    # Note attachments
    path("attachments/", ClinicalNoteAttachmentListCreateView.as_view(), name="clinicalnoteattachment-list-create"),
    path("attachments/<int:pk>/", ClinicalNoteAttachmentRUDView.as_view(), name="clinicalnoteattachment-rud"),
]
