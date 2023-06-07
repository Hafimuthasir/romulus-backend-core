from rest_framework import serializers
from Core.models import *
from django.contrib.auth.hashers import make_password
from Core.serializers import AssetsSerializer


class StaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Company
        fields = ['username', 'number', 'password', 'company_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        validated_data['user_type'] = 'staff'
        staff = Company.objects.create(**validated_data)
        return staff


class GetStaffSerializer(serializers.ModelSerializer):
    assets_incharge = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'username', 'assets_incharge', 'number']

    def get_assets_incharge(self, obj):
        assets = obj.assets_incharge.all()
        asset_serializer = AssetsSerializer(assets, many=True)
        return asset_serializer.data


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    created_month = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Payments
        fields = "__all__"

    # def create(self, validated_data):
    #     validated_data['created_month'] = datetime.now().strftime("%B")
    #     return super().create(validated_data)
    def to_internal_value(self, data):
        if 'created_month' not in data:
            data['created_month'] = datetime.now().strftime("%B")
        return super().to_internal_value(data)