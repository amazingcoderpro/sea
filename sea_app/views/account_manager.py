from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app import models
from sea_app.serializers import account_manager
from sea_app.filters import account_manager as account_manager_filters


class PinterestAccountView(generics.ListAPIView):
    """pinterest账号和对应board"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = account_manager.PinterestAccountSerializer
    # pagination_class = PNPagination
    filter_backends = (account_manager_filters.PinterestAccountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RuleView(generics.ListAPIView):
    """规则"""
    queryset = models.Rule.objects.all()
    serializer_class = account_manager.RuleSerializer
    # pagination_class = PNPagination
    # filter_backends = (filters.UserFilter, DjangoFilterBackend)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    # filterset_fields = ("nickname",)