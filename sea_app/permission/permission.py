from rest_framework.permissions import BasePermission
from sea_app import models


class UserPermission(BasePermission):

    method = ["GET", "PUT", "POST"]

    def has_object_permission(self, request, view, obj):
        if obj == request.user and request.method in self.method:
            return True
        if not obj.parent or obj.parent != request.user:
            return False
        return True


# class RolePermission(BasePermission):
#
#     def has_object_permission(self, request, view, obj):
#         if obj.user_id == request.user.id:
#             return True
#         return False


class RulePermission(BasePermission):

    def has_object_permission(self, request, view, obj):
            if obj.user_id == request.user.id:
                return True
            return False