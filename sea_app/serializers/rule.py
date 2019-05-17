from rest_framework import serializers
from sea_app import models


class RuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Rule
        fields = ("id",
                  "start_time",
                  "end_time",
                  "interval_time",
                  "scan_sign",
                  "scan",
                  "sale_sign",
                  "sale",
                  "tag",
                  "state",
                  "state",
                  "create_time",
                  "update_time"
        )