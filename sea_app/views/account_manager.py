from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app import models
from sea_app.serializers import account_manager
from sea_app.filters import account_manager as account_manager_filters
from sea_app.pageNumber.pageNumber import PNPagination



class PinterestAccountView(generics.ListAPIView):
    """pinterest账号和对应board"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = account_manager.PinterestAccountSerializer
    filter_backends = (account_manager_filters.PinterestAccountFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)


class RuleView(generics.ListCreateAPIView):
    """规则"""
    queryset = models.Rule.objects.all()
    serializer_class = account_manager.RuleSerializer
    pagination_class = PNPagination
    # filter_backends = (filters.UserFilter, DjangoFilterBackend)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    # filterset_fields = ("nickname",)

    # def create(self, request, *args, **kwargs):
    #     print(request.data)
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid()
    #     print(serializer.errors)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response("1111")