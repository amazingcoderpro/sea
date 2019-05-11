from rest_framework.filters import BaseFilterBackend
from django.db.models import Q


class UserFilter(BaseFilterBackend):
    """用户列表过滤"""
    def filter_queryset(self, request, queryset, view):
        parent_id = request.user.parent_id
        if parent_id:
            return queryset.filter(Q(parent_id=parent_id) | Q(id=parent_id))
        return queryset.filter(id=request.user.id)
