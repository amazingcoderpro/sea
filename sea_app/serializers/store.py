from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from sea_app import models
import json


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Store
        fields = ("name", "url", "email", "visitors", "scan", "sale", "user", "authorized", "create_time")
        # extra_kwargs = {
        #     'platform': {'write_only': False, 'read_only': True},
        # }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(StoreSerializer, self).create(validated_data)