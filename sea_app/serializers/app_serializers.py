from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from sea_app import models


class StoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Store
        exclude = ("user",)