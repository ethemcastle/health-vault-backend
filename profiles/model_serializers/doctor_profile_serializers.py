from rest_framework import serializers


class DoctorProfileWriteSerializer(serializers.Serializer):
    specialization = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)
    hospital_affiliation = serializers.CharField(required=False, allow_blank=True)


class DoctorProfileReadSerializer(serializers.Serializer):
    specialization = serializers.CharField()
    license_number = serializers.CharField(allow_null=True, allow_blank=True)
    hospital_affiliation = serializers.CharField(allow_null=True, allow_blank=True)
