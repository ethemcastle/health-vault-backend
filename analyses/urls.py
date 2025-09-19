from django.urls import path

from analyses.model_views.analysis_view import (
    AnalysisListCreateView, AnalysisRUDView,
)
from analyses.model_views.analysis_result_view import (
    AnalysisResultListCreateView, AnalysisResultRUDView,
)

app_name = "analyses"

urlpatterns = [
    # Analyses (uploads + OCR)
    path("", AnalysisListCreateView.as_view(), name="analysis-list-create"),
    path("<int:pk>/", AnalysisRUDView.as_view(), name="analysis-rud"),

    # Structured results
    path("results/", AnalysisResultListCreateView.as_view(), name="analysisresult-list-create"),
    path("results/<int:pk>/", AnalysisResultRUDView.as_view(), name="analysisresult-rud"),
]
