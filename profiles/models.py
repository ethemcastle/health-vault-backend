from django.conf import settings
from django.db import models

from authentication.models import User
from core.models import BaseModel


class PatientProfile(BaseModel):
    class Meta:
        verbose_name = "Patient Profile"
        verbose_name_plural = "Patient Profiles"
        db_table = "profile_patient"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    family_history = models.TextField(blank=True, null=True)
    risk_factors = models.TextField(blank=True, null=True)
    insurance_provider = models.CharField(max_length=128, blank=True, null=True)


class DoctorProfile(BaseModel):
    class Meta:
        verbose_name = "Doctor Profile"
        verbose_name_plural = "Doctor Profiles"
        db_table = "profile_doctor"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    specialization = models.CharField(max_length=128, blank=True, null=True)
    license_number = models.CharField(max_length=64, unique=True, blank=True, null=True)
    hospital_affiliation = models.CharField(max_length=128, blank=True, null=True)


class PatientDoctorConsent(BaseModel):
    """
    Explicit patient consent for a doctor to view data and trends.
    """
    class Scope(models.TextChoices):
        ANALYSES = "ANALYSES", "Lab analyses"
        NOTES = "NOTES", "Clinical notes"
        REMINDERS = "REMINDERS", "Reminders"
        ALL = "ALL", "All data"

    class Meta:
        verbose_name = "Patient-Doctor Consent"
        verbose_name_plural = "Patient-Doctor Consents"
        db_table = "patient_doctor_consent"
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor", "scope"],
                condition=models.Q(is_active=True),
                name="uniq_active_consent",
            )
        ]
        indexes = [
            models.Index(fields=["patient", "doctor", "is_active"]),
        ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consents_as_patient")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consents_as_doctor")
    scope = models.CharField(max_length=16, choices=Scope.choices, default=Scope.ANALYSES)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
