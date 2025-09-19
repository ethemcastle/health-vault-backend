from core.api_views import BaseLCAPIView, BaseRUDAPIView
from core.permissions import CanWritePatientData
from notes.model_serializers.clinical_note_serializers import ClinicalNoteReadSerializer, ClinicalNoteWriteSerializer
from notes.models import ClinicalNote


class ClinicalNoteListCreateView(BaseLCAPIView):
    queryset = ClinicalNote.objects.select_related("patient", "doctor").all()
    read_serializer_class = ClinicalNoteReadSerializer
    write_serializer_class = ClinicalNoteWriteSerializer
    list_read_serializer_class = ClinicalNoteReadSerializer
    permission_classes = [CanWritePatientData]  # doctors with consent can write; patients can read theirs


class ClinicalNoteRUDView(BaseRUDAPIView):
    queryset = ClinicalNote.objects.select_related("patient", "doctor").all()
    read_serializer_class = ClinicalNoteReadSerializer
    write_serializer_class = ClinicalNoteWriteSerializer
    permission_classes = [CanWritePatientData]
