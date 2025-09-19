from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import BasePermission


class CanView(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        obj = ContentType.objects.get_for_model(view.queryset.model)
        return user and user.has_perm(obj.app_label + '.view_' + obj.model)


class CanAdd(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        obj = ContentType.objects.get_for_model(view.queryset.model)
        return user and user.has_perm(obj.app_label + '.add_' + obj.model)


class CanChange(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        obj = ContentType.objects.get_for_model(view.queryset.model)
        return user and user.has_perm(obj.app_label + '.change_' + obj.model)


class CanDelete(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        obj = ContentType.objects.get_for_model(view.queryset.model)
        return user and user.has_perm(obj.app_label + '.delete_' + obj.model)
