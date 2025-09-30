from core.api_views import BaseLCAPIView, BaseRUDAPIView
from analyses.models import AnalysisResult
from analyses.model_serializers.analysis_result_serializers import AnalysisResultReadSerializer, AnalysisResultWriteSerializer
from core.permissions import CanWritePatientData


class AnalysisResultListCreateView(BaseLCAPIView):
    queryset = AnalysisResult.objects.select_related("analysis", "analysis__patient").all()
    read_serializer_class = AnalysisResultReadSerializer
    write_serializer_class = AnalysisResultWriteSerializer
    list_read_serializer_class = AnalysisResultReadSerializer
    permission_classes = [CanWritePatientData]


class AnalysisResultRUDView(BaseRUDAPIView):
    queryset = AnalysisResult.objects.select_related("analysis", "analysis__patient").all()
    read_serializer_class = AnalysisResultReadSerializer
    write_serializer_class = AnalysisResultWriteSerializer
    permission_classes = [CanWritePatientData]
