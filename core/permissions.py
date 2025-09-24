# authentication/permissions.py
from __future__ import annotations
from typing import Any, Optional

from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request

from authentication.const import ADMIN, DOCTOR, PATIENT
from profiles.models import PatientDoctorConsent


def _is_authenticated(user: Any) -> bool:
    return bool(user and not isinstance(user, AnonymousUser) and user.is_authenticated)


def _has_role(user: Any, roles: list[str]) -> bool:
    return bool(_is_authenticated(user) and getattr(getattr(user, "group", None), "name", None) in roles)


class IsAdmin(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return _has_role(request.user, [ADMIN])


class IsDoctor(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return _has_role(request.user, [DOCTOR])


class IsPatient(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return _has_role(request.user, [PATIENT])


class IsOwner(BasePermission):
    """
    Object must have a `user` FK pointing to request.user.
    """
    def has_permission(self, request: Request, view) -> bool:
        return _is_authenticated(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class IsOwnerByField(BasePermission):
    """
    Same as IsOwner but lets you specify the FK field name on the object that references the owner user.
    Example: IsOwnerByField("patient") for models where `.patient` is a FK to User.
    """
    owner_field: str

    def __init__(self, owner_field: str = "user") -> None:
        self.owner_field = owner_field

    def has_permission(self, request: Request, view) -> bool:
        return _is_authenticated(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        user_id = getattr(request.user, "id", None)
        owner = getattr(obj, self.owner_field, None)
        owner_id = getattr(owner, "id", None)
        return owner_id == user_id


class IsAdminOrOwner(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return _is_authenticated(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        return _has_role(request.user, [ADMIN]) or getattr(obj, "user_id", None) == getattr(request.user, "id", None)


class IsAdminOrDoctorForCreate(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        if not _is_authenticated(request.user):
            return False

        if request.method == "POST":
            return _has_role(request.user, [ADMIN, DOCTOR])
        if request.method == "GET":
            return _has_role(request.user, [ADMIN, DOCTOR])

        return _has_role(request.user, [ADMIN])


class IsParticipantInConsentOrAdmin(BasePermission):
    """
    For PatientDoctorConsent objects:
    - Admins allowed
    - Patient or Doctor mentioned in the consent allowed
    """
    def has_permission(self, request: Request, view) -> bool:
        return _is_authenticated(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if _has_role(request.user, [ADMIN]):
            return True
        uid = getattr(request.user, "id", None)
        return getattr(obj, "patient_id", None) == uid or getattr(obj, "doctor_id", None) == uid


def _doctor_has_consent(doctor_id: Optional[int], patient_id: Optional[int]) -> bool:
    if not doctor_id or not patient_id:
        return False
    return PatientDoctorConsent.objects.filter(
        doctor_id=doctor_id, patient_id=patient_id, is_active=True
    ).exists()


class CanReadPatientData(BasePermission):
    """
    Allows:
      - Admins
      - The patient themselves
      - Doctors WITH active consent from the patient
    Works for objects that expose either:
      - `patient` FK to User, or
      - `user` FK to User, or
      - nested `.analysis.patient`, `.note.patient`, etc. (pass `resolve_patient` in view attr if needed)
    """
    def has_permission(self, request: Request, view) -> bool:
        return _is_authenticated(request.user)

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if _has_role(request.user, [ADMIN]):
            return True

        # find patient user id: try common attributes, else custom resolver on the view
        patient_user_id = None
        for path in ("patient_id", "user_id", "patient.user_id"):
            try:
                parts = path.split(".")
                cur = obj
                for p in parts:
                    cur = getattr(cur, p)
                patient_user_id = cur
                break
            except Exception:
                continue

        if patient_user_id is None:
            resolver = getattr(view, "resolve_patient_user_id", None)
            if callable(resolver):
                patient_user_id = resolver(obj)

        req_user_id = getattr(request.user, "id", None)

        # patient themself
        if patient_user_id == req_user_id:
            return True

        # doctor with consent
        if _has_role(request.user, [DOCTOR]):
            return _doctor_has_consent(doctor_id=req_user_id, patient_id=patient_user_id)

        return False


class CanWritePatientData(BasePermission):
    """
    Allows writes by:
      - Admins
      - The patient themself (for their resources)
      - Doctors WITH consent from patient
    For create actions (no object yet), we look for `patient` in request.data.
    """
    def has_permission(self, request: Request, view) -> bool:
        if not _is_authenticated(request.user):
            return False
        if request.method in SAFE_METHODS:
            return True

        if _has_role(request.user, [ADMIN]):
            return True

        # creating/updating: figure out patient target from payload when object is absent
        patient_id = None
        data = getattr(request, "data", {}) or {}
        if isinstance(data, dict):
            patient_id = data.get("patient") or data.get("user")  # common keys

        if patient_id is None:
            # for partial updates without patient field, object-level check will decide
            return True

        # patient themself
        if getattr(request.user, "id", None) == int(patient_id):
            return True

        # doctor with consent to that patient
        if _has_role(request.user, [DOCTOR]):
            return _doctor_has_consent(doctor_id=getattr(request.user, "id", None), patient_id=int(patient_id))

        return False

    def has_object_permission(self, request: Request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return CanReadPatientData().has_object_permission(request, view, obj)

        if _has_role(request.user, [ADMIN]):
            return True

        # determine patient user id from the object
        patient_user_id = None
        for path in ("patient_id", "user_id", "patient.user_id"):
            try:
                parts = path.split(".")
                cur = obj
                for p in parts:
                    cur = getattr(cur, p)
                patient_user_id = cur
                break
            except Exception:
                continue

        req_user_id = getattr(request.user, "id", None)

        if patient_user_id == req_user_id:
            return True

        if _has_role(request.user, [DOCTOR]):
            return _doctor_has_consent(doctor_id=req_user_id, patient_id=patient_user_id)

        return False
