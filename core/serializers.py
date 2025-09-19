from rest_framework import serializers

from core.const import ERROR_TYPE, MESSAGE, IS_SUCCESS, ERRORS, RESULT


class ResponseSerializer(serializers.Serializer):
    is_success = serializers.BooleanField()
    message = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    errors = serializers.ListField(child=serializers.CharField(max_length=255), required=False, default=list)

    @staticmethod
    def success(message: str = "") -> dict:
        return {IS_SUCCESS: True, MESSAGE: message, ERRORS: []}

    @staticmethod
    def fail(message: str, errors=None, error_type: str = "", **kwargs) -> dict:
        if errors is None:
            errors = []
        return {IS_SUCCESS: False, MESSAGE: message, ERRORS: errors, ERROR_TYPE: error_type}


class ResponseWithResultSerializer(ResponseSerializer):
    result = serializers.JSONField()

    @staticmethod
    def success(result, message="") -> dict:
        return {IS_SUCCESS: True, MESSAGE: message, ERRORS: [], RESULT: result}

    @staticmethod
    def fail(message: str, errors=None, error_type: str = "", **kwargs) -> dict:
        if errors is None:
            errors = []
        return {IS_SUCCESS: False, MESSAGE: message, ERRORS: errors, ERROR_TYPE: error_type, RESULT: None}
