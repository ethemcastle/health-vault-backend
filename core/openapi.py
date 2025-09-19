from rest_framework import serializers

class SuccessEnvelope(serializers.Serializer):
    message = serializers.CharField(required=False)
    result = serializers.JSONField(required=False)

class ErrorEnvelope(serializers.Serializer):
    message = serializers.CharField()
    error_type = serializers.CharField(required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
