from rest_framework.permissions import BasePermission
from sea_app import models


class UserPermission(BasePermission):

    message = '无权限访问'

    def has_object_permission(self, request, view, obj):
        if not obj.parent or obj.parent != request.user:
            return False
        return True