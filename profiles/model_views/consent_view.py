from core.api_views import BaseLCAPIView, BaseRUDAPIView
from core.permissions import IsParticipantInConsentOrAdmin
from profiles.models import PatientDoctorConsent
from profiles.model_serializers.consent_serializers import ConsentReadSerializer, ConsentWriteSerializer


class ConsentListCreateView(BaseLCAPIView):
    queryset = PatientDoctorConsent.objects.select_related("patient", "doctor").all()
    read_serializer_class = ConsentReadSerializer
    write_serializer_class = ConsentWriteSerializer
    list_read_serializer_class = ConsentReadSerializer
    permission_classes = [IsParticipantInConsentOrAdmin]


class ConsentRUDView(BaseRUDAPIView):
    queryset = PatientDoctorConsent.objects.select_related("patient", "doctor").all()
    read_serializer_class = ConsentReadSerializer
    write_serializer_class = ConsentWriteSerializer
    permission_classes = [IsParticipantInConsentOrAdmin]
