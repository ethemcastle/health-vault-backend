from core.api_views import BaseLCAPIView, BaseRUDAPIView
from core.permissions import CanWritePatientData
from profiles.models import PatientProfile
from profiles.model_serializers.patient_profile_serializers import PatientProfileReadSerializer, PatientProfileWriteSerializer


class PatientProfileListCreateView(BaseLCAPIView):
    queryset = PatientProfile.objects.select_related("user").all()
    read_serializer_class = PatientProfileReadSerializer
    write_serializer_class = PatientProfileWriteSerializer
    list_read_serializer_class = PatientProfileReadSerializer
    permission_classes = [CanWritePatientData]


class PatientProfileRUDView(BaseRUDAPIView):
    queryset = PatientProfile.objects.select_related("user").all()
    read_serializer_class = PatientProfileReadSerializer
    write_serializer_class = PatientProfileWriteSerializer
    permission_classes = [CanWritePatientData]
