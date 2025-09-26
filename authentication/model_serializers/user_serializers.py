from typing import Any, Dict, Optional
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, Group
from django.db import transaction, models
from rest_framework import serializers

from authentication.const import DOCTOR, PATIENT, ADMIN
from profiles.model_serializers.doctor_profile_serializers import DoctorProfileReadSerializer
from profiles.model_serializers.patient_profile_serializers import PatientProfileReadSerializer

User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    doctor_profile = serializers.SerializerMethodField()
    patient_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name",
            "phone", "birthday", "gender",
            "role", "doctor_profile", "patient_profile",
            "date_created", "date_last_updated",
        ]
        read_only_fields = fields

    @staticmethod
    def get_role(obj: User) -> Optional[str]:
        return getattr(getattr(obj, "group", None), "name", None)

    @staticmethod
    def get_doctor_profile(obj: User) -> Optional[dict]:
        dp = getattr(obj, "doctor_profile", None)
        if not dp:
            return None
        return DoctorProfileReadSerializer(dp).data

    @staticmethod
    def get_patient_profile(obj: User) -> Optional[dict]:
        pp = getattr(obj, "patient_profile", None)
        if not pp:
            return None
        return PatientProfileReadSerializer(pp).data


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "password", "first_name", "last_name",
            "birthday", "phone", "gender",
            "group", "is_active",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data: Dict[str, Any]) -> AbstractBaseUser:
        password: str = validated_data.pop("password")
        user: AbstractBaseUser = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance: AbstractBaseUser, validated_data: Dict[str, Any]) -> AbstractBaseUser:
        password: str = validated_data.pop("password", "")
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserSelfUpdateSerializer(serializers.ModelSerializer):
    """
    For non-admins updating their own account.
    NOTE: no role/group changes here.
    """
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "first_name", "last_name",
            "phone", "birthday", "gender",
            "password",
        ]

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance



class AdminUserWriteSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[ADMIN, DOCTOR, PATIENT], required=True, write_only=True)
    doctor_profile = serializers.DictField(required=False, write_only=True)
    patient_profile = serializers.DictField(required=False, write_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name", "last_name",
            "phone", "birthday", "gender",
            "password",
            "role",
            "doctor_profile", "patient_profile",
        ]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context.get("request")
        requester_role = getattr(getattr(getattr(request, "user", None), "group", None), "name", None)

        role = attrs.get("role")

        # Doctors may only create Patients
        if requester_role == DOCTOR:
            if role != PATIENT:
                raise serializers.ValidationError({"role": "Doctors can only create Patient accounts."})
            if "doctor_profile" in attrs:
                raise serializers.ValidationError({"doctor_profile": "Not allowed when creator is Doctor."})

        # Prevent weird mixes
        if role == DOCTOR and "patient_profile" in attrs:
            raise serializers.ValidationError({"patient_profile": "Not allowed when role is Doctor."})
        if role == PATIENT and "doctor_profile" in attrs:
            raise serializers.ValidationError({"doctor_profile": "Not allowed when role is Patient."})

        return attrs

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> User:
        from profiles.models import DoctorProfile, PatientProfile

        password = validated_data.pop("password")
        role = validated_data.pop("role")
        doctor_data = validated_data.pop("doctor_profile", None)
        patient_data = validated_data.pop("patient_profile", None)

        user = User(**validated_data)
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.save()

        grp = Group.objects.get(name=role)
        user.group = grp
        user.save(update_fields=["group"])

        if role == DOCTOR:
            dp, _ = DoctorProfile.objects.get_or_create(user=user)
            if doctor_data:
                for k, v in doctor_data.items():
                    setattr(dp, k, v)
                dp.save()
        else:  # PATIENT
            pp, _ = PatientProfile.objects.get_or_create(user=user)
            if patient_data:
                for k, v in patient_data.items():
                    setattr(pp, k, v)
                pp.save()

        return user

    @transaction.atomic
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        from profiles.models import DoctorProfile, PatientProfile

        request = self.context.get("request")
        requester_role = getattr(getattr(getattr(request, "user", None), "group", None), "name", None)

        password = validated_data.pop("password", None)
        role = validated_data.pop("role", None)
        doctor_data = validated_data.pop("doctor_profile", None)
        patient_data = validated_data.pop("patient_profile", None)

        # Doctors cannot change a user's role to anything but Patient
        if requester_role == DOCTOR and role and role != PATIENT:
            raise serializers.ValidationError({"role": "Doctors cannot change role to non-Patient."})

        for k, v in validated_data.items():
            setattr(instance, k, v)

        if password:
            instance.set_password(password)

        if role:
            grp = Group.objects.get(name=role)
            instance.group = grp

        instance.save()

        # Maintain profiles
        effective_role = role or getattr(getattr(instance, "group", None), "name", None)

        if effective_role == DOCTOR:
            dp, _ = DoctorProfile.objects.get_or_create(user=instance)
            if doctor_data:
                for k, v in doctor_data.items():
                    setattr(dp, k, v)
                dp.save()

        if effective_role == PATIENT:
            pp, _ = PatientProfile.objects.get_or_create(user=instance)
            if patient_data:
                for k, v in patient_data.items():
                    setattr(pp, k, v)
                pp.save()

        return instance

    # Render output using the read serializer so we include derived `role` + nested profiles
    def to_representation(self, instance: User) -> Dict[str, Any]:
        from .user_serializers import UserReadSerializer
        return UserReadSerializer(instance, context=self.context).data