from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated

from authentication.const import ADMIN, DOCTOR
from core.api_views import BaseLCAPIView, BaseRUDAPIView
from authentication.model_serializers.user_serializers import (
    UserReadSerializer,
    UserSelfUpdateSerializer,
    AdminUserWriteSerializer,
)
from core.permissions import IsAdmin, IsAdminOrOwner, IsAdminOrDoctorForCreate
from profiles.models import PatientDoctorConsent

User = get_user_model()



class UserListCreateView(BaseLCAPIView):
    queryset = User.objects.select_related("group").all()
    read_serializer_class = UserReadSerializer
    write_serializer_class = AdminUserWriteSerializer
    list_read_serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrDoctorForCreate]

    def get_queryset(self) -> QuerySet[User]:
        qs = super().get_queryset()
        user = self.request.user
        role = getattr(getattr(user, "group", None), "name", None)

        # Admin: full list
        if role == ADMIN:
            role_param = self.request.query_params.get("role")
            if role_param:
                qs = qs.filter(group__name=role_param)
            q = self.request.query_params.get("q")
            if q:
                qs = qs.filter(email__icontains=q)
            return qs

        # Doctor: only their patients (assuming Consent model links them)
        if role == DOCTOR:
            patient_ids = PatientDoctorConsent.objects.filter(
                doctor=user, is_active=True
            ).values_list("patient_id", flat=True)
            return qs.filter(id__in=patient_ids)

        # Patients cannot list other users
        return qs.none()


class UserRUDView(BaseRUDAPIView):
    queryset = User.objects.select_related("group").all()
    read_serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_serializer_class(self):
        # Admin can fully edit (role, profiles); others can edit self basics only
        if self.request and self.request.method in ("PUT", "PATCH"):
            is_admin = getattr(getattr(self.request.user, "group", None), "name", None) == ADMIN
            return AdminUserWriteSerializer if is_admin else UserSelfUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet[User]:
        qs = super().get_queryset()
        user = self.request.user
        is_admin = getattr(getattr(user, "group", None), "name", None) == ADMIN
        return qs if is_admin else qs.filter(id=user.id)