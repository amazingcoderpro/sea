from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from sea_app import models
from sea_app.serializers import rule


class RuleView(generics.ListAPIView):
    queryset = models.Rule.objects.all()
    serializer_class = rule.RuleSerializer
    # pagination_class = PNPagination
    # filter_backends = (filters.UserFilter, DjangoFilterBackend)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)
    # filterset_fields = ("nickname",)