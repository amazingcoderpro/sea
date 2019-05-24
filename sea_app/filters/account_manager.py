from rest_framework.filters import BaseFilterBackend
from django.db.models import Q

from sea_app import models


class PinterestAccountFilter(BaseFilterBackend):
    """pinterest账号列表过滤"""

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class BoardListFilter(BaseFilterBackend):
    """board列表过滤"""

    def filter_queryset(self, request, queryset, view):
        account_id = request.query_params.dict().get("pinterest_account_id")
        if account_id:
            return queryset.filter(Q(pinterest_account_id=account_id))
        else:
            return queryset.filter(pinterest_account__user=request.user)


class PinListFilter(BaseFilterBackend):
    """board列表过滤"""

    def filter_queryset(self, request, queryset, view):
        board_id = request.query_params.dict().get("board")
        if board_id:
            return queryset.filter(board_id=board_id)
        else:
            return queryset.filter(board__pinterest_account__user=request.user)


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

        account_id = request.query_params.get("account_id", '')
        if account_id:
            border_list = models.Board.objects.filter(pinterest_account=account_id).values_list("id")
            border_list = map(lambda x: x[0], border_list)
            return queryset.filter(board_id__in=border_list)
        for filter_key in self.filter_keys.keys():
            val = request.query_params.get(filter_key, '')
            if val is not '':
                if filter_key == "board_list":
                    filte_kwargs[self.filter_keys[filter_key]] = eval(val)
                    continue
                filte_kwargs[self.filter_keys[filter_key]] = val
        queryset = queryset.filter(**filte_kwargs)
        return queryset


class ProductCountFilter(BaseFilterBackend):
    """pinterest账号列表过滤"""

    filter_keys = {
        "begin_time": "update_time__gte",
        "end_time": "update_time__lte",
        "product__name": "product__name__contains",
        "store": "store"
    }

    def filter_queryset(self, request, queryset, view):
        filte_kwargs = {}
        for filter_key in self.filter_keys.keys():
            val = request.query_params.get(filter_key, '')
            if val is not '':
                filte_kwargs[self.filter_keys[filter_key]] = val
        queryset = queryset.filter(**filte_kwargs)
        return queryset