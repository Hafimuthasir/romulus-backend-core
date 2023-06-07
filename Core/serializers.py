from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

class CompanySerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data.get('password'))
        return super().update(instance, validated_data)
    



class CompanyLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        try:
            company = Company.objects.get(username=username)
        except:
            raise serializers.ValidationError('Invalid credentials')

        # if not company.is_admin:
        #     raise serializers.ValidationError('Invalid credentials')
        
        if company.check_password(password):
            attrs['company'] = company
        else:
            raise serializers.ValidationError('Invalid credentials')

        return attrs

class AssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assets
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetLocations
        fields = '__all__'

