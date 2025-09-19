from core.api_views import BaseLCAPIView, BaseRUDAPIView
from core.permissions import IsAdmin, IsOwnerByField
from notifications.models import Notification
from notifications.model_serializers.notification_serializers import NotificationReadSerializer, NotificationWriteSerializer


class NotificationListCreateView(BaseLCAPIView):
    queryset = Notification.objects.select_related("user").all()
    read_serializer_class = NotificationReadSerializer
    write_serializer_class = NotificationWriteSerializer
    list_read_serializer_class = NotificationReadSerializer
    permission_classes = [IsAdmin]


class NotificationRUDView(BaseRUDAPIView):
    queryset = Notification.objects.select_related("user").all()
    read_serializer_class = NotificationReadSerializer
    write_serializer_class = NotificationWriteSerializer
    permission_classes = [IsAdmin | IsOwnerByField]