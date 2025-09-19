from core.api_views import BaseLCAPIView, BaseRUDAPIView
from analyses.models import Analysis
from analyses.model_serializers.analysis_serializers import AnalysisReadSerializer, AnalysisWriteSerializer
from core.permissions import CanWritePatientData


class AnalysisListCreateView(BaseLCAPIView):
    queryset = Analysis.objects.select_related("patient", "uploaded_by").prefetch_related("results").all()
    read_serializer_class = AnalysisReadSerializer
    write_serializer_class = AnalysisWriteSerializer
    list_read_serializer_class = AnalysisReadSerializer
    permission_classes = [CanWritePatientData]


class AnalysisRUDView(BaseRUDAPIView):
    queryset = Analysis.objects.select_related("patient", "uploaded_by").prefetch_related("results").all()
    read_serializer_class = AnalysisReadSerializer
    write_serializer_class = AnalysisWriteSerializer
    permission_classes = [CanWritePatientData]
