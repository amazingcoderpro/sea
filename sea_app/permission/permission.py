from rest_framework.permissions import BasePermission
from sea_app import models


class UserPermission(BasePermission):

    method = ["GET", "PUT", "POST"]

    def has_object_permission(self, request, view, obj):
        print(obj,request.user)
        if obj == request.user:
            return True
        else:
            return False


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