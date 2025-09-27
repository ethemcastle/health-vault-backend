from django.conf import settings
from django.db import models
from core.models import BaseModel


class Analysis(BaseModel):
    class Meta:
        verbose_name = "Analysis"
        verbose_name_plural = "Analysis"
        db_table = "analysis"

    class Source(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analyses")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="uploaded_analyses")
    source = models.CharField(max_length=10, choices=Source.choices)
    title = models.CharField(max_length=200, blank=True, null=True)

    file = models.FileField(upload_to="analyses/")
    ocr_text = models.TextField(blank=True, null=True)
    ocr_language = models.CharField(max_length=16, default="eng")

    report_date = models.DateField(blank=True, null=True)
    order_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title or f"Analysis #{self.id}"


class AnalysisResult(BaseModel):
    class Meta:
        verbose_name = "Analysis Result"
        verbose_name_plural = "Analysis Results"
        db_table = "analysis_result"
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name="results")
    test_name = models.CharField(max_length=200)
    value = models.CharField(max_length=64, blank=True, null=True)
    unit = models.CharField(max_length=32, blank=True, null=True)
    reference_range = models.CharField(max_length=64, blank=True, null=True)
    measured_at = models.DateField(blank=True, null=True)
