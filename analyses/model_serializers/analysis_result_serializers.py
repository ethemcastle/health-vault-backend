from rest_framework import serializers
from analyses.models import AnalysisResult



class AnalysisResultReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = ["id", "test_name", "value", "unit", "reference_range", "measured_at", "date_created", "date_last_updated"]


class AnalysisResultWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = [
            "id", "analysis", "test_name", "value", "unit",
            "reference_range",
            "measured_at",
        ]
        read_only_fields = ["id"]
