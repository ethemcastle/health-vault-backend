from core.api_views import BaseLCAPIView, BaseRUDAPIView
from core.permissions import CanWritePatientData
from reminders.models import Reminder
from reminders.model_serializers.reminder_serializers import ReminderReadSerializer, ReminderWriteSerializer


class ReminderListCreateView(BaseLCAPIView):
    queryset = Reminder.objects.select_related("patient", "created_by").all()
    read_serializer_class = ReminderReadSerializer
    write_serializer_class = ReminderWriteSerializer
    list_read_serializer_class = ReminderReadSerializer
    permission_classes = [CanWritePatientData]  # doctor/admin can create for patient; patient reads theirs


class ReminderRUDView(BaseRUDAPIView):
    queryset = Reminder.objects.select_related("patient", "created_by").all()
    read_serializer_class = ReminderReadSerializer
    write_serializer_class = ReminderWriteSerializer
    permission_classes = [CanWritePatientData]
