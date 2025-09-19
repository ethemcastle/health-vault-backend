from rest_framework import serializers
from analyses.models import AnalysisResult


class AnalysisResultReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = [
            "id", "analysis", "name", "value", "unit",
            "reference_low", "reference_high", "reference_text",
            "measured_at", "sort_key",
            "date_created", "date_last_updated",
        ]
        read_only_fields = ["id", "date_created", "date_last_updated"]


class AnalysisResultWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = [
            "id", "analysis", "name", "value", "unit",
            "reference_low", "reference_high", "reference_text",
            "measured_at", "sort_key",
        ]
        read_only_fields = ["id"]
