from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from sea_app import models
from config import SHOPIFY_CONFIG
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
            'name': {'write_only': False, 'read_only': True},
            'url': {'write_only': False, 'read_only': True},
            'email': {'write_only': False, 'read_only': True},
            'visitors': {'write_only': False, 'read_only': True},
            'scan': {'write_only': False, 'read_only': True},
            'timezone': {'write_only': False, 'read_only': True},
            'country': {'write_only': False, 'read_only': True},
            'city': {'write_only': False, 'read_only': True},

            # 'store_view_id': {'write_only': True, 'read_only': True},
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super(StoreSerializer, self).create(validated_data)

    def to_representation(self, instance):
        data = super(StoreSerializer, self).to_representation(instance)
        data["url_format"] = instance.url + SHOPIFY_CONFIG["utm_format"]
        return data