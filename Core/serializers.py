from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.dateformat import format
import pytz
from django.db.models import Sum
from .models import *
from romulus_staff.serializers import *

class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = (
            'trade_name', 'administrative_office', 'other_office', 'gstin',
            'monthly_purchase_cost', 'monthly_purchase_quantity', 'total_outstanding',
            'total_purchase_cost', 'total_purchase_quantity', 'city', 'pin_code'
        )

class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = '__all__'
        # fields = (
        #     'trade_name', 'administrative_office', 'other_office', 'gstin',
        #     'monthly_purchase_cost', 'monthly_purchase_quantity', 'total_outstanding',
        #     'total_purchase_cost', 'total_purchase_quantity', 'city', 'pin_code'
        # )


class UserSerializer(serializers.ModelSerializer):
    company_info = CompanyInfoSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id','username', 'email', 'role', 'number', 'password', 'company_info')

    def create(self, validated_data):
        # company_info_data = validated_data.pop('company_info', {})
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class GetCompanySerializer(serializers.ModelSerializer):
    company_info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','username', 'email', 'number', 'is_active', 'company_info']

    def get_company_info(self, obj):
        current_month = datetime.now().month
        current_year = datetime.now().year
        try:
            info = CompanyInfo.objects.get(company_id=obj.id)
            # total_price = Order.objects.filter(company=obj.id, order_status='Delivered', created_at__year=current_year, created_at__month=current_month).aggregate(total_price=Sum('total_price'))['total_price']
            # total_quantity = Order.objects.filter(company=obj.id, order_status='Delivered', created_at__year=current_year, created_at__month=current_month).aggregate(total_quantity=Sum('quantity'))['total_quantity']

            company_info_data = CompanyInfoSerializer(info).data
            # company_info_data['monthly_purchase_cost'] = total_price if total_price is not None else 0
            # company_info_data['monthly_purchase_quantity'] = total_quantity if total_quantity is not None else 0

            company_info_data['monthly_purchase_cost'] = 0
            company_info_data['monthly_purchase_quantity'] = 0
            return company_info_data
        except CompanyInfo.DoesNotExist:
            return None
        



    



class CompanyLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        print('hello')
        try:
            user = User.objects.get(username=username)
            print(user,'ddddddd')
        except:
            raise serializers.ValidationError('Invalid credentials')

        # if not company.is_admin:
        #     raise serializers.ValidationError('Invalid credentials')

        if user.check_password(password):
            if not user.is_active:
                print('ddd')
                raise serializers.ValidationError('Your Company has blocked or deleted')
            if user.company_id is not None:
                company = User.objects.get(id=user.company_id_id)
                
                if company.is_active:
                    attrs['company'] = user
                else:
                    raise serializers.ValidationError('Your Company has blocked or deleted')
            else:
                if user.is_active :
                    attrs['company'] = user
                else:
                    raise serializers.ValidationError('Your Company has blocked or deleted')
        else:
            raise serializers.ValidationError('Invalid credentials')

        return attrs

class AssetsSerializer(serializers.ModelSerializer):
    staff_incharge_name = serializers.CharField(source='staff_incharge.username', read_only=True)
    last_order_date = serializers.SerializerMethodField(read_only=True)
    location_name = serializers.CharField(source='assetLocation.location',read_only=True)

    class Meta:
        model = Assets
        fields = '__all__'
        read_only_fields = ['staff_incharge_name','last_order_date','location_name']
        
        # extra_kwargs = {
        #     'asset_type': {'read_only': True}  
        # }

    def get_last_order_date(self, asset):
        last_order = asset.order_set.last()  
        if last_order:
            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_created_at = last_order.created_at.astimezone(ist_tz)
            formatted_date = ist_created_at.strftime('%d %B %I:%M %p')
            return formatted_date
            # print(last_order.created_at)
            # return last_order.created_at
        
        return None
    
    
    
    


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLocations
        fields = '__all__'



class TotalizerReadingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalizerReadings
        fields = ['created_at', 'added_by', 'company', 'asset', 'reading', 'image']

class RomulusAssetsSerializer(serializers.ModelSerializer):
    last_totalizer_updated = serializers.SerializerMethodField(read_only=True)
    is_totalizer_updated = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = RomulusAssets
        fields = '__all__'

    def get_is_totalizer_updated(self,asset):
        last_totalizer = asset.totalizerreadings_set.last()
        if last_totalizer:
            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_created_at = last_totalizer.created_at.astimezone(ist_tz).date()
            today = timezone.now().astimezone(ist_tz).date()
            return ist_created_at == today
        return False
    
    def get_last_totalizer_updated(self, asset):
        last_totalizer = asset.totalizerreadings_set.last()
        if last_totalizer:
            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_created_at = last_totalizer.created_at.astimezone(ist_tz)
            formatted_date = ist_created_at.strftime('%d %B %I:%M %p')
            return formatted_date
        return None
    

class StaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)
    company_id = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['username', 'number', 'password', 'company_id', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        # validated_data['user_type'] = 'staff'
        staff = User.objects.create(**validated_data)
        return staff
    
    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        return super().update(instance, validated_data)

class OrderDistributionSerializer(serializers.ModelSerializer):
    # distribution = OrderDistributionSerializer(many=True, read_only=True)
    asset_name = serializers.SerializerMethodField(read_only=True)
    asset_type = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = OrderDistribution
        fields = '__all__'

    def get_asset_name(self, instance):
        return instance.asset.assetName
    
    def get_asset_type(self, instance):
        return instance.asset.typeOfAsset

class RomulusDeliverySerializer(serializers.ModelSerializer):
    distribution = OrderDistributionSerializer(many=True, read_only=True)
    class Meta:
        model = RomulusDeliveries
        fields = '__all__'


class OrderDetailsSerializer(serializers.ModelSerializer):
    deliveries = RomulusDeliverySerializer(many=True, read_only=True)
    distribution = OrderDistributionSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'