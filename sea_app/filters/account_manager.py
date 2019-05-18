from rest_framework.filters import BaseFilterBackend
from django.db.models import Q


class PinterestAccountFilter(BaseFilterBackend):
    """pinterest账号列表过滤"""

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class ProductFilter(BaseFilterBackend):
    """pinterest账号列表过滤"""

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(store=request.query_params["store"])


class RuleFilter(BaseFilterBackend):
    """规则过滤"""

    filter_keys = {
        "board_list": "board_id__in",
        "tag": "tag",
        "begin_time": "create_time__gte",
        "end_time": "create_time__lte",
    }

    def filter_queryset(self, request, queryset, view):
        filte_kwargs = {"state__in": [0, 2, 3, 4, 5]}
        for filter_key in self.filter_keys.keys():
            val = request.query_params.get(filter_key, '')
            if val is not '':
                if filter_key == "board_list":
                    filte_kwargs[self.filter_keys[filter_key]] = eval(val)
                    continue
                filte_kwargs[self.filter_keys[filter_key]] = val
        queryset = queryset.filter(**filte_kwargs)
        return queryset