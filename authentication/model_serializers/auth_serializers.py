from typing import Any, Dict
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, Group
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.const import PATIENT, DOCTOR, ADMIN
from profiles.model_serializers.doctor_profile_serializers import DoctorProfileWriteSerializer
from profiles.model_serializers.patient_profile_serializers import PatientProfileWriteSerializer


User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    """
    Single endpoint:
      - role: "Doctor" or "Patient"
      - doctor_profile: only when role=Doctor
      - patient_profile: only when role=Patient
    Doctor creation is restricted to Admins (security check here).
    """
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=[DOCTOR, PATIENT], write_only=True)
    doctor_profile = DoctorProfileWriteSerializer(write_only=True, required=False)
    patient_profile = PatientProfileWriteSerializer(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email", "password",
            "first_name", "last_name",
            "phone", "birthday", "gender",
            "role",
            "doctor_profile", "patient_profile",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        role: str = attrs.get("role")
        request = self.context.get("request")

        # Only Admin can create Doctor users
        if role == DOCTOR:
            is_admin = bool(
                request
                and getattr(request.user, "is_authenticated", False)
                and getattr(getattr(request.user, "group", None), "name", None) == ADMIN
            )
            if not is_admin:
                raise serializers.ValidationError({"role": "Only Admin can create Doctor accounts."})
            # Optional: require at least one doctor field
            if not attrs.get("doctor_profile"):
                attrs["doctor_profile"] = {}

        if role == PATIENT and attrs.get("patient_profile") is None:
            attrs["patient_profile"] = {}

        return attrs

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> User:
        role: str = validated_data.pop("role")
        doctor_data: Dict[str, Any] = validated_data.pop("doctor_profile", {}) or {}
        patient_data: Dict[str, Any] = validated_data.pop("patient_profile", {}) or {}
        password: str = validated_data.pop("password")

        user: User = User(**validated_data)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save()

        # attach Group by name (assumes groups seeded via post_migrate)
        try:
            group = Group.objects.get(name=role)
            user.group = group
            user.save(update_fields=["group"])
        except Group.DoesNotExist:
            raise serializers.ValidationError({"role": "Role group not found. Run migrations/seed groups first."})

        # Create corresponding profile
        if role == DOCTOR:
            from profiles.models import DoctorProfile
            DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    "specialization": doctor_data.get("specialization") or "",
                    "license_number": doctor_data.get("license_number") or None,
                    "hospital_affiliation": doctor_data.get("hospital_affiliation") or "",
                },
            )
        elif role == PATIENT:
            from profiles.models import PatientProfile
            PatientProfile.objects.get_or_create(
                user=user,
                defaults={
                    "family_history": patient_data.get("family_history") or "",
                    "risk_factors": patient_data.get("risk_factors") or "",
                    "insurance_provider": patient_data.get("insurance_provider") or "",
                },
            )

        return user


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        data: Dict[str, Any] = super().validate(attrs)
        user = self.user  # AbstractBaseUser
        data["user"] = {
            "id": user.id,
            "email": getattr(user, "email", ""),
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "phone": getattr(user, "phone", None),
            "birthday": getattr(user, "birthday", None),
            "gender": getattr(user, "gender", None),
            "group": getattr(user, "group_id", None),
            "is_staff": getattr(user, "is_staff", False),
            "is_superuser": getattr(user, "is_superuser", False),
        }
        return data
