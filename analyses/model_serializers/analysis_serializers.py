# analyses/model_serializers/analysis_serializers.py
from __future__ import annotations
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from analyses.model_serializers.analysis_result_serializers import AnalysisResultReadSerializer
from analyses.models import Analysis, AnalysisResult
from analyses.services.ocr import save_ocr_output

User = get_user_model()


class AnalysisReadSerializer(serializers.ModelSerializer):
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    uploaded_by_email = serializers.EmailField(source="uploaded_by.email", read_only=True)
    results = AnalysisResultReadSerializer(many=True, read_only=True)

    class Meta:
        model = Analysis
        fields = [
            "id", "title", "source",
            "patient", "patient_email",
            "uploaded_by", "uploaded_by_email",
            "file", "ocr_text", "ocr_language",
            "report_date",
            "results",
            "date_created", "date_last_updated",
        ]
        read_only_fields = ["id", "uploaded_by", "ocr_text", "report_date", "results", "date_created", "date_last_updated"]


class AnalysisWriteSerializer(serializers.ModelSerializer):
    """
    Doctor upload:
      - patient (user id)
      - file (PDF/JPG/PNG)
      - title (optional)
      - ocr_language (optional; default 'eng')
    """
    patient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    file = serializers.FileField(required=True)

    class Meta:
        model = Analysis
        fields = ["patient", "title", "file", "ocr_language"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        f = attrs.get("file")
        if not f:
            raise serializers.ValidationError({"file": "File is required."})
        # basic size/type constraints if you want (optional)
        return attrs

    @transaction.atomic
    def create(self, validated_data: Dict[str, Any]) -> Analysis:
        request = self.context.get("request")
        user = getattr(request, "user", None)

        analysis = Analysis.objects.create(
            patient=validated_data["patient"],
            uploaded_by=user if user and user.is_authenticated else None,
            source=Analysis.Source.DOCTOR if user else Analysis.Source.PATIENT,
            title=validated_data.get("title"),
            file=validated_data["file"],
            ocr_language=validated_data.get("ocr_language") or "eng",
        )

        # Synchronous OCR now (simple; swap to Celery later if you want)
        try:
            save_ocr_output(analysis, lang=analysis.ocr_language)
        except Exception as e:
            # Keep the upload even if OCR fails; you can retry later.
            # If you prefer to hard-fail, raise serializers.ValidationError(str(e))
            pass

        return analysis
