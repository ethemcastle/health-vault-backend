from rest_framework import serializers


class PatientProfileReadSerializer(serializers.Serializer):
    family_history = serializers.CharField(allow_null=True, allow_blank=True)
    risk_factors = serializers.CharField(allow_null=True, allow_blank=True)
    insurance_provider = serializers.CharField(allow_null=True, allow_blank=True)


class PatientProfileWriteSerializer(serializers.Serializer):
    family_history = serializers.CharField(required=False, allow_blank=True)
    risk_factors = serializers.CharField(required=False, allow_blank=True)
    insurance_provider = serializers.CharField(required=False, allow_blank=True)
