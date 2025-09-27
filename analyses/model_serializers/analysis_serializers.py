from __future__ import annotations

from django.db import transaction
from rest_framework import serializers

from analyses.model_serializers.analysis_result_serializers import AnalysisResultReadSerializer
import re
from django.contrib.auth import get_user_model

import fitz

from analyses.models import Analysis, AnalysisResult

User = get_user_model()


class AnalysisReadSerializer(serializers.ModelSerializer):
    results = AnalysisResultReadSerializer(many=True, read_only=True)
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    uploaded_by_email = serializers.EmailField(source="uploaded_by.email", read_only=True)

    class Meta:
        model = Analysis
        fields = [
            "id", "title", "source",
            "patient", "patient_email",
            "uploaded_by", "uploaded_by_email",
            "file", "ocr_text", "ocr_language",
            "report_date", "results",
            "date_created", "date_last_updated", "order_id"
        ]
        read_only_fields = ["ocr_text", "results", "report_date"]


class AnalysisWriteSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    file = serializers.FileField(required=True)

    class Meta:
        model = Analysis
        fields = ["patient", "title", "file"]

    @staticmethod
    def _extract_text_from_pdf(pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        return text

    @staticmethod
    def _extract_order_id(text: str) -> str | None:
        """
        Try to capture order id from PDF text.
        Adjust regex if labs use a different label.
        """
        pattern = re.compile(r"Order\s*ID[:\s]+([A-Za-z0-9\-\_/]+)", re.IGNORECASE)
        match = pattern.search(text)
        return match.group(1).strip() if match else None

    @staticmethod
    def _parse_results(text: str):
        results = []
        pattern = re.compile(
            r"^(?P<name>[A-Za-z0-9 ()/*]+)\s+(?P<value>[<>]?\s*\d+[.,]?\d*)\s*(?P<unit>[A-Za-z/%µμ]+)?\s+(?P<ref>[\d<>\-– ]+[A-Za-z/%µμ ]*)",
            re.MULTILINE,
        )
        for match in pattern.finditer(text):
            results.append(
                {
                    "test_name": match.group("name").strip(" *"),
                    "value": match.group("value").replace(" ", ""),
                    "unit": match.group("unit") or "",
                    "reference_range": match.group("ref").strip(),
                }
            )
        return results


    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        # Save file first
        analysis = Analysis.objects.create(
            patient=validated_data["patient"],
            uploaded_by=user if user and user.is_authenticated else None,
            source=Analysis.Source.DOCTOR if user else Analysis.Source.PATIENT,
            title=validated_data.get("title") or "Imported Lab Report",
            file=validated_data["file"],
        )

        # Extract text from PDF
        text = self._extract_text_from_pdf(analysis.file.path)

        # Extract order_id
        order_id = self._extract_order_id(text)
        if not order_id:
            raise serializers.ValidationError({"file": "Could not find Order ID in PDF."})

        # Prevent duplicates
        if Analysis.objects.filter(order_id=order_id).exists():
            raise serializers.ValidationError({"file": f"Analysis with order_id {order_id} already exists."})

        analysis.order_id = order_id
        analysis.ocr_text = text
        analysis.save(update_fields=["order_id", "ocr_text", "date_last_updated"])

        # Extract and save results
        rows = self._parse_results(text)
        if rows:
            bulk = [
                AnalysisResult(
                    analysis=analysis,
                    test_name=row["test_name"],
                    value=row["value"],
                    unit=row["unit"],
                    reference_range=row["reference_range"],
                )
                for row in rows
            ]
            AnalysisResult.objects.bulk_create(bulk)

        return analysis