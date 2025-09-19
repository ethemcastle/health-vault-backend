from core.api_views import BaseLCAPIView, BaseRUDAPIView
from core.permissions import IsAdmin, IsAdminOrOwner
from profiles.models import DoctorProfile
from profiles.model_serializers.doctor_profile_serializers import DoctorProfileReadSerializer, DoctorProfileWriteSerializer


class DoctorProfileListCreateView(BaseLCAPIView):
    queryset = DoctorProfile.objects.select_related("user").all()
    read_serializer_class = DoctorProfileReadSerializer
    write_serializer_class = DoctorProfileWriteSerializer
    list_read_serializer_class = DoctorProfileReadSerializer
    permission_classes = [IsAdmin]


class DoctorProfileRUDView(BaseRUDAPIView):
    queryset = DoctorProfile.objects.select_related("user").all()
    read_serializer_class = DoctorProfileReadSerializer
    write_serializer_class = DoctorProfileWriteSerializer
    permission_classes = [IsAdminOrOwner]
