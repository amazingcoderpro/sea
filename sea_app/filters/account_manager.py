import datetime

from rest_framework.filters import BaseFilterBackend
from django.db.models import Q

from sea_app import models


class PinterestAccountFilter(BaseFilterBackend):
    """pinterest账号列表过滤"""

    filter_keys = {
        "authorized": "authorized__in",
    }

    def filter_queryset(self, request, queryset, view):

        filte_kwargs = {"user_id": request.user.id}
        for filter_key in self.filter_keys.keys():
            val = request.query_params.get(filter_key, '')
            if val != '':
                if type(eval(val)) == list:
                    filte_kwargs[self.filter_keys[filter_key]] = eval(val)
                    continue
                filte_kwargs[self.filter_keys[filter_key]] = val
        if not filte_kwargs:
            return []
        queryset = queryset.filter(**filte_kwargs)
        return queryset


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
        filte_kwargs = {"state__in": [-1, 0, 1, 2, 3, 4], "user_id": request.user.id}

        account_id = request.query_params.get("account_id", '')
        if account_id:
            border_list = models.Board.objects.filter(pinterest_account=account_id).values_list("id")
            border_list = map(lambda x: x[0], border_list)
            return queryset.filter(board_id__in=border_list).order_by('-create_time')
        for filter_key in self.filter_keys.keys():
            val = request.query_params.get(filter_key, '')
            if val is not '':
                if filter_key == "board_list":
                    filte_kwargs[self.filter_keys[filter_key]] = eval(val)
                    continue
                filte_kwargs[self.filter_keys[filter_key]] = val
        queryset = queryset.filter(**filte_kwargs)
        return queryset.order_by('-create_time')


class ProductCountFilter(BaseFilterBackend):
    """pinterest账号列表过滤"""

    filter_keys = {
        "publish_begin_time": "publish_time__gte",
        "publish_end_time": "publish_time__lte",
        "product_category_list": "product_category_id__in"
    }

    def filter_queryset(self, request, queryset, view):
        filte_kwargs = {"store": models.Store.objects.filter(user=request.user).first()}
        for filter_key in self.filter_keys.keys():
            val = request.query_params.get(filter_key, '')
            if val is not '':
                if filter_key == "product_category_list":
                    filte_kwargs[self.filter_keys[filter_key]] = eval(val)
                filte_kwargs[self.filter_keys[filter_key]] = val
        if not filte_kwargs:
            return []

        name = request.query_params.get("product__name", '')
        name = ".*" + name.replace(" ", ".*") + ".*"
        filte_kwargs["name__iregex"] = name
        print("###", filte_kwargs)
        queryset = queryset.filter(**filte_kwargs)

        return queryset


class ReportFilter(BaseFilterBackend):
    filter_keys = {
        # "rule__state": "rule__state__in",
        "state": "state__in",
    }

    def filter_queryset(self, request, queryset, view):
        # filte_kwargs = {"rule__user_id": request.user.id,}
        # for filter_key in self.filter_keys.keys():
        #     val = request.query_params.get(filter_key, '')
        #     if val != '':
        #         if filter_key == "product__sku":
        #             filte_kwargs[self.filter_keys[filter_key]] = val
        #             continue
        #         if type(eval(val)) == list:
        #             filte_kwargs[self.filter_keys[filter_key]] = eval(val)
        #             continue
        #         filte_kwargs[self.filter_keys[filter_key]] = val
        # if not filte_kwargs:
        #     return []
        # 获取请求参数
        user_id = request.user.id
        state = request.query_params.get("state", '')
        query_key = request.query_params.get("query_key", '')
        start_time = request.query_params.get("publish_time_start", '')
        end_time = request.query_params.get("publish_time_end", '')
        if start_time and isinstance(start_time, str):
            try:
                start_time = datetime.datetime(*map(int, start_time.split('-')))
            except:
                start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        if end_time and isinstance(end_time, str):
            try:
                end_time = datetime.datetime(*map(int, end_time.split('-')))
            except:
                end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

        queryset = queryset.filter(Q(rule__user_id=user_id),
                                   Q(product__sku__icontains=query_key)|Q(board__name__icontains=query_key)|Q(board__pinterest_account__nickname__icontains=query_key))
        if state:
            queryset = queryset.filter(state__in=eval(state))
        if start_time and end_time:
            queryset = queryset.filter(execute_time__range=(start_time,end_time))
        record_manager = request.query_params.get("record_manager", '')
        if record_manager:
            queryset = queryset.order_by("execute_time")
        else:
            queryset = queryset.order_by("-finished_time")
        return queryset


class GetUserFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        username = request.query_params.get("username", '')
        return queryset.filter(username=username)


class GetCategoryFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(store__user=request.user)
