from rest_framework import serializers

from authentication.const import DOCTOR, PATIENT
from authentication.model_serializers.user_serializers import UserReadSerializer
from profiles.models import PatientDoctorConsent


class ConsentReadSerializer(serializers.ModelSerializer):
    doctor = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

    class Meta:
        model = PatientDoctorConsent
        fields = ["id", "doctor", "patient", "is_active", "scope", "date_created", "date_last_updated"]

    @staticmethod
    def get_doctor(obj):
        return UserReadSerializer(obj.doctor).data

    @staticmethod
    def get_patient(obj):
        return UserReadSerializer(obj.patient).data


class ConsentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDoctorConsent
        fields = ["id", "patient", "doctor", "scope", "expires_at", "is_active"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["patient"].id == attrs["doctor"].id:
            raise serializers.ValidationError("Patient and doctor must be different users.")
        if attrs["doctor"].group.name != DOCTOR:
            raise serializers.ValidationError("User is not a doctor.")
        if attrs["patient"].group.name != PATIENT:
            raise serializers.ValidationError("User is not a patient.")
        return attrs
