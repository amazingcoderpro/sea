from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from sea_app import models
from sea_app.serializers import store
from sea_app.filters import store as store_filter
from sea_app.pageNumber.pageNumber import PNPagination


class StoreView(generics.ListCreateAPIView):
    """店铺 增 列表展示"""
    queryset = models.Store.objects.all()
    serializer_class = store.StoreSerializer
    pagination_class = PNPagination
    filter_backends = (store_filter.StoreFilter, DjangoFilterBackend)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    filterset_fields = ("name", "email")


class StoreOperView(generics.RetrieveUpdateDestroyAPIView):
    """店铺 删 该 查"""
    queryset = models.Store.objects.all()
    serializer_class = store.StoreSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)