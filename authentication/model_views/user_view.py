from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework.permissions import IsAuthenticated

from core.api_views import BaseLCAPIView, BaseRUDAPIView
from authentication.model_serializers.user_serializers import (
    UserReadSerializer,
    UserSelfUpdateSerializer,
    AdminUserWriteSerializer,
)
from core.permissions import IsAdmin, IsAdminOrOwner

User = get_user_model()


class UserListCreateView(BaseLCAPIView):
    """
    List all users (Admin). Create via admin if you want, but your public signup handles normal users.
    """
    queryset = User.objects.select_related("group").all()
    read_serializer_class = UserReadSerializer
    write_serializer_class = AdminUserWriteSerializer
    list_read_serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    # Optional: enable filtering by role ?role=Doctor|Patient|Admin
    def get_queryset(self) -> QuerySet[User]:
        qs = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(group__name=role)
        search = self.request.query_params.get("q")
        if search:
            qs = qs.filter(email__icontains=search)
        return qs


class UserRUDView(BaseRUDAPIView):
    """
    Retrieve/Update/Delete a user.
    - Admin can retrieve/update/delete any user.
    - A user can retrieve/update themself (no role/group change).
    """
    queryset = User.objects.select_related("group").all()
    read_serializer_class = UserReadSerializer
    # write serializer will be chosen dynamically
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_serializer_class(self):
        # Admins can use admin write serializer (role/profile updates).
        # Owners use self-update serializer.
        if self.request and self.request.method in ("PUT", "PATCH"):
            if self.request.user and getattr(getattr(self.request.user, "group", None), "name", None) == "Admin":
                return AdminUserWriteSerializer
            return UserSelfUpdateSerializer
        return super().get_serializer_class()

    # (Optional) ensure non-admins can only act on themselves at the queryset level too
    def get_queryset(self) -> QuerySet[User]:
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return qs.none()
        is_admin = getattr(getattr(user, "group", None), "name", None) == "Admin"
        if is_admin:
            return qs
        return qs.filter(id=user.id)
