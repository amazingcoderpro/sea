from django.db import transaction
from rest_framework import serializers

from sea_app import models


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Board
        fields = "__all__"


class PinterestAccountSerializer(serializers.ModelSerializer):
    board_pinterest_account = BoardSerializer(many=True, read_only=True)

    class Meta:
        model = models.PinterestAccount
        fields = (
            "id",
            "account_uri",
            "name",
            "email",
            "type",
            "state",
            "add_time",
            "create_time",
            "update_time",
            "user",
            "board_pinterest_account"
        )


class RuleScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RuleSchedule
        fields = "__all__"


class RuleSerializer(serializers.ModelSerializer):
    schedule_rule = RuleScheduleSerializer(many=True, read_only=True)
    scan_sign_name = serializers.CharField(source="get_scan_sign_display", read_only=True)
    sale_sign_name = serializers.CharField(source="get_sale_sign_display", read_only=True)
    baord_name = serializers.CharField(source="board.pinterest_account.name", read_only=True)

    class Meta:
        model = models.Rule
        fields = ("id",
                  "scan_sign",
                  "scan_sign_name",
                  "sale_sign_name",
                  "scan",
                  "sale_sign",
                  "sale",
                  "product_list",
                  "tag",
                  "state",
                  "schedule_rule",
                  "board",
                  "create_time",
                  "start_time",
                  "end_time",
                  "state",
                  "baord_name"
        )

    def create(self, validated_data):
        with transaction.atomic():
            validated_data["user"] = self.context["request"].user
            schedule_rule_list = eval(self.context["request"].data["schedule_rule"])
            rule_instance = super(RuleSerializer, self).create(validated_data)
            for row in schedule_rule_list:
                row["rule"] = rule_instance
                models.RuleSchedule.objects.create(**row)
        return rule_instance

    def update(self, instance, validated_data):
        schedule_rule_list = eval(self.context["request"].data["schedule_rule"])
        with transaction.atomic():
            rule_instance = super(RuleSerializer, self).update(instance, validated_data)
            models.RuleSchedule.objects.filter(rule=instance).delete()
            for row in schedule_rule_list:
                row["rule"] = rule_instance
                models.RuleSchedule.objects.create(**row)
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = "__all__"
