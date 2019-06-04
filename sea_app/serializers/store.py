from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from sea_app import models
import json


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Store
        fields = ("id",
                  "name",
                  "url",
                  "email",
                  "visitors",
                  "scan",
                  "sale",
                  "timezone",
                  "country",
                  "city",
                  "store_view_id")
        extra_kwargs = {
            'scan': {'write_only': False, 'read_only': False},
            # 'user': {'write_only': False, 'read_only': False},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(StoreSerializer, self).create(validated_data)