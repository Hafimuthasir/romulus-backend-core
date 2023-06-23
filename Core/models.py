from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime

class CompanyManager(BaseUserManager):

    def create_user(self, email, username, password=None):
        # if not username:
        #     raise ValueError('Company must have a name')
        # if not city:
        #     raise ValueError('Company must have a city')
        # if not pin_code:
        #     raise ValueError('Company must have a pin code')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            # city=city,
            # pin_code=pin_code,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):

        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            # city=city,
            # pin_code=pin_code,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Company(AbstractBaseUser):
    username = models.CharField(max_length=255,unique=True)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=10,blank=True)
    is_admin = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, default='manager')
    number = models.CharField(max_length=12)

    monthly_purchase_cost = models.IntegerField(blank=True,null=True)
    monthly_purchase_quantity = models.IntegerField(blank=True,null=True)
    total_outstanding = models.IntegerField(blank=True,null=True)
    total_purchase_cost = models.IntegerField(blank=True,null=True)
    total_purchase_quantity = models.IntegerField(blank=True,null=True)

    #staff additional information
    company_id = models.IntegerField(blank=True,null=True)

    legal_name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255,blank=True)
    effective_date_of_registration = models.DateField(auto_now=False,null=True)
    constitution_of_bussiness = models.CharField(max_length=100,blank=True)
    gstin_uin_status = models.CharField(max_length=100,blank=True)
    taxpayer_type = models.CharField(max_length=100,blank=True)
    administrative_office = models.TextField(blank=True)
    other_office = models.TextField(blank=True)
    principle_place = models.TextField(blank=True)
    adhaar_authenticated_status = models.CharField(max_length=50,default=False,blank=True)
    ekyc_status = models.CharField(max_length=100,blank=True)
    gstin = models.CharField(max_length=100)
    additional_trade_name = models.TextField(blank=True)

    USERNAME_FIELD = 'username'

    objects = CompanyManager()

    def __str__(self):
        return self.username

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True
    

class Assets(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    assetCapacity = models.IntegerField()
    staff_incharge = models.ForeignKey(Company,on_delete=models.CASCADE, related_name='assets_incharge', blank=True,null=True)
    assetLocation = models.CharField(max_length=255,null=True)
    assetName = models.CharField(max_length=255,unique=True)
    assetPincode = models.IntegerField()
    assetRegistrationNumber = models.CharField(max_length=255,blank=True)
    assetState = models.CharField(max_length=255,blank=True)
    fuelType = models.CharField(max_length=255,default='Diesel',blank=True)
    typeOfAsset = models.CharField(max_length=255,null=True)

class AssetLocations(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    location = models.TextField(blank=True)
    location2 = models.TextField(blank=True)
    location3 = models.TextField(blank=True)


class Order(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(Company,on_delete=models.CASCADE,related_name='ordered_user')
    quantity = models.IntegerField()
    asset = models.ForeignKey(Assets,on_delete=models.CASCADE)
    diesel_price = models.FloatField()
    total_price = models.FloatField()
    order_status = models.CharField(max_length=100,default='ordered')
    created_at = models.DateTimeField(auto_now=True)
    ordered_user_type = models.CharField(max_length=100)
    order_type = models.CharField(max_length=100,default='client')
    # payment_status = models.CharField(default=True)


class Payments(models.Model):
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100) # paid purchase
    order = models.ForeignKey(Order,on_delete=models.PROTECT)
    payment_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    created_month = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100,blank=True)
    transaction_id = models.CharField(max_length=100,blank=True)



