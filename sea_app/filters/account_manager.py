from rest_framework.filters import BaseFilterBackend
from django.db.models import Q


class PinterestAccountFilter(BaseFilterBackend):
    """pinterest账号列表过滤"""

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)
