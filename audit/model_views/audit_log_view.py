from rest_framework.permissions import IsAuthenticated
from core.api_views import BaseListAPIView, BaseRetrieveAPIView
from audit.models import AuditLog
from audit.model_serializers.audit_log_serializers import AuditLogReadSerializer
from core.permissions import IsAdmin


class AuditLogListView(BaseListAPIView):
    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogReadSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class AuditLogRetrieveView(BaseRetrieveAPIView):
    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogReadSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
