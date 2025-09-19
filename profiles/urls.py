from django.urls import path

from profiles.model_views.patient_profile_view import (
    PatientProfileListCreateView, PatientProfileRUDView,
)
from profiles.model_views.doctor_profile_view import (
    DoctorProfileListCreateView, DoctorProfileRUDView,
)
from profiles.model_views.consent_view import (
    ConsentListCreateView, ConsentRUDView,
)

app_name = "profiles"

urlpatterns = [
    # Patient profiles
    path("patients/", PatientProfileListCreateView.as_view(), name="patientprofile-list-create"),
    path("patients/<int:pk>/", PatientProfileRUDView.as_view(), name="patientprofile-rud"),

    # Doctor profiles
    path("doctors/", DoctorProfileListCreateView.as_view(), name="doctorprofile-list-create"),
    path("doctors/<int:pk>/", DoctorProfileRUDView.as_view(), name="doctorprofile-rud"),

    # Consents
    path("consents/", ConsentListCreateView.as_view(), name="consent-list-create"),
    path("consents/<int:pk>/", ConsentRUDView.as_view(), name="consent-rud"),
]
