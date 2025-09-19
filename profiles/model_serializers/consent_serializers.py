from rest_framework import serializers
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
        # optional: ensure patient != doctor
        if attrs["patient_id"] == attrs["doctor_id"]:
            raise serializers.ValidationError("Patient and doctor must be different users.")
        return attrs
