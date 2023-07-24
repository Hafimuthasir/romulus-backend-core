from Core.models import *
from rest_framework import serializers


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = RomulusDeliveries
        fields = "__all__"

class DistributionSerializer(serializers.ModelSerializer):
    asset_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderDistribution
        fields = "__all__"

    # def get_company_id(self, obj):
    #     return obj.delivery.order.company_id

    def get_asset_name(self,obj):
        return obj.asset.assetName




