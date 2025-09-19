from core.api_views import BaseLCAPIView, BaseRUDAPIView
from core.permissions import CanWritePatientData
from notes.models import ClinicalNoteAttachment
from notes.model_serializers.clinical_note_attachment_serializers import ClinicalNoteAttachmentReadSerializer, ClinicalNoteAttachmentWriteSerializer


class ClinicalNoteAttachmentListCreateView(BaseLCAPIView):
    queryset = ClinicalNoteAttachment.objects.select_related("note", "note__patient", "note__doctor").all()
    read_serializer_class = ClinicalNoteAttachmentReadSerializer
    write_serializer_class = ClinicalNoteAttachmentWriteSerializer
    list_read_serializer_class = ClinicalNoteAttachmentReadSerializer
    permission_classes = [CanWritePatientData]


class ClinicalNoteAttachmentRUDView(BaseRUDAPIView):
    queryset = ClinicalNoteAttachment.objects.select_related("note", "note__patient", "note__doctor").all()
    read_serializer_class = ClinicalNoteAttachmentReadSerializer
    write_serializer_class = ClinicalNoteAttachmentWriteSerializer
    permission_classes = [CanWritePatientData]
