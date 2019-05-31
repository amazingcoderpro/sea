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
            "email",
            "type",
            "state",
            "authorized",
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
    baord_name = serializers.CharField(source="board.board_uri", read_only=True)
    account_name = serializers.CharField(source="board.pinterest_account.account_uri", read_only=True)

    class Meta:
        model = models.Rule
        # depth = 2
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
                  "baord_name",
                  "account_name"
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


class ProductHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductHistoryData
        fields = "__all__"


class PublishRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublishRecord
        depth = 1
        fields = "__all__"


class PinterestAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PinterestAccount
        fields = (
            "id",
            "account_uri",
            "nickname",
            "email",
            "type",
            # "state",
            "description",
            "create_time",
        )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        instance = super(PinterestAccountCreateSerializer, self).create(validated_data)
        instance.user = self.context["request"].user
        instance.save()
        return instance


class RuleStatusSerializer(serializers.ModelSerializer):
    """修改规则状态"""
    class Meta:
        model = models.Rule
        # depth = 2
        fields = ("id", "state",)

