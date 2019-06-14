from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from sea_app import models
from sea_app.serializers import store
from sea_app.filters import store as store_filter
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.permission import permission


class StoreView(generics.ListAPIView):
    """店铺 展示展示"""
    queryset = models.Store.objects.all()
    serializer_class = store.StoreSerializer
    filter_backends = (store_filter.StoreFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class StoreOperView(generics.UpdateAPIView):
    """店铺 改"""
    queryset = models.Store.objects.all()
    serializer_class = store.StoreSerializer
    permission_classes = (IsAuthenticated, permission.RulePermission)
    authentication_classes = (JSONWebTokenAuthentication,)