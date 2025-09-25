from rest_framework import serializers

from authentication.const import DOCTOR, PATIENT
from profiles.models import PatientDoctorConsent


class ConsentReadSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    doctor_email = serializers.EmailField(source="doctor.email", read_only=True)

    class Meta:
        model = PatientDoctorConsent
        fields = [
            "id", "patient", "patient_email",
            "doctor", "doctor_email",
            "scope", "expires_at", "is_active",
            "date_created", "date_last_updated",
        ]
        read_only_fields = ["id", "patient_email", "doctor_email", "date_created", "date_last_updated"]


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
