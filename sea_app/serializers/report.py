# -*- coding: utf-8 -*-
from rest_framework import serializers

from sea_app import models


class SunAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.PinterestAccount
        depth = 1
        fields = ("id", "following", "follower", "state", "updateTime")
