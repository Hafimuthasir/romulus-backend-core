from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from datetime import datetime
from django.utils import timezone
import os
import pytz
import uuid

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


class User(AbstractBaseUser):
    username = models.CharField(max_length=255,unique=True)
    email = models.EmailField(blank=True)
    is_admin = models.BooleanField(default=False)
    role = models.CharField(max_length=10, default='manager')
    number = models.CharField(max_length=12)
    is_active = models.BooleanField(default=True)

    #staff additional information
    company_id = models.ForeignKey('self', blank=True, null=True, on_delete=models.DO_NOTHING)


    USERNAME_FIELD = 'username'

    objects = CompanyManager()

    def delete(self, *args, **kwargs):
        self.is_active = False  
        self.save()

    def permanent_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.username

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True
    

class CompanyInfo(models.Model):
    company = models.OneToOneField(User, on_delete=models.CASCADE)
    trade_name = models.CharField(max_length=255, blank=True)
    administrative_office = models.TextField(blank=True)
    other_office = models.TextField(blank=True)
    gstin = models.CharField(max_length=100)
    monthly_purchase_cost = models.IntegerField(blank=True, null=True)
    monthly_purchase_quantity = models.IntegerField(blank=True, null=True)
    total_outstanding = models.IntegerField(default=0, blank=True, null=True)
    total_purchase_cost = models.IntegerField(blank=True, null=True)
    total_purchase_quantity = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=10, blank=True)
    diesel_price = models.FloatField(null=True)
    discount_price = models.FloatField(null=True)



class AssetLocations(models.Model):
    company = models.ForeignKey(User,on_delete=models.CASCADE)
    location = models.TextField(blank=True)    

class Assets(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    assetCapacity = models.IntegerField()
    staff_incharge = models.ForeignKey(User,on_delete=models.CASCADE, related_name='assets_incharge', blank=True,null=True)
    assetLocation = models.ForeignKey(AssetLocations,on_delete=models.CASCADE, blank=True,null=True)
    assetName = models.CharField(max_length=255,unique=True)
    assetPincode = models.IntegerField()
    assetRegistrationNumber = models.CharField(max_length=255,blank=True)
    assetState = models.CharField(max_length=255,blank=True)
    fuelType = models.CharField(max_length=255,default='Diesel',blank=True)
    typeOfAsset = models.CharField(max_length=255,null=True)
    is_active = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        self.is_active = False  # Disable the company instead of deleting
        self.save()





class Order(models.Model):
    company = models.ForeignKey(User,on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='ordered_user')
    quantity = models.IntegerField()
    asset = models.ForeignKey(Assets,on_delete=models.CASCADE)
    diesel_price = models.FloatField()
    total_price = models.FloatField()
    order_status = models.CharField(max_length=100,default='ordered')
    created_at = models.DateTimeField(auto_now=True)
    ordered_user_type = models.CharField(max_length=100)
    order_type = models.CharField(max_length=100,default='client')
    discount_price = models.FloatField(null=True)
    saved_amount = models.FloatField(null=True)
    by_admin = models.BooleanField(default=False)
    ordered_admin = models.ForeignKey(User,on_delete=models.PROTECT,related_name='ordered_admin',null=True,blank=True)
    order_id = models.CharField(max_length=50, unique=True, editable=False)
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         tz = pytz.timezone('Asia/Kolkata')
    #         self.created_at = timezone.localtime(timezone.now(), tz)
    #     super().save(*args, **kwargs)
    # payment_status = models.CharField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only generate the order_id for new instances
            super().save(*args, **kwargs)

            # Generate unique order ID based on auto-generated ID
            prefix = 'CL' if self.order_type == 'client' else 'RM'
            formatted_date = timezone.now().strftime("%d%m%y")  # Format as DDMMYY
            order_id = f'{prefix}{formatted_date}N{self.id}'

            self.order_id = order_id
            self.save(update_fields=['order_id'])
        else:
            super().save(*args, **kwargs)


class Payments(models.Model):
    company = models.ForeignKey(User,on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100) # paid purchase
    order = models.ForeignKey(Order,on_delete=models.PROTECT,blank=True,null=True)
    payment_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    created_month = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100,blank=True)
    transaction_id = models.CharField(max_length=100,blank=True)
    is_active = models.BooleanField(default=True)
    payment_id = models.CharField(max_length=50, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk: 
            super().save(*args, **kwargs)

      
            prefix = 'PD' if self.payment_type == 'paid' else 'PU'
            formatted_date = timezone.now().strftime("%d%m%y")  
            payment_id = f'{prefix}{formatted_date}{self.id}'

            self.payment_id = payment_id
            self.save(update_fields=['payment_id'])
        else:
            super().save(*args, **kwargs)
    


    def delete(self, *args, **kwargs):
        self.is_active = False 
        self.save()


class TotalizerReadings(models.Model):

    def upload_to(instance, filename):
        filename_base, filename_ext = os.path.splitext(filename)
        current_datetime = timezone.now().strftime('%Y_%m_%d_%H_%M_%S')
        unique_id = str(uuid.uuid4().hex[:2])
        return f'TotalizerReadings/{current_datetime}_{unique_id}{filename_ext}'

    created_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User,on_delete=models.PROTECT)
    company = models.ForeignKey(User,on_delete=models.PROTECT, related_name='company')
    asset = models.ForeignKey(Assets,on_delete=models.PROTECT)
    reading = models.IntegerField()
    image = models.FileField(upload_to=upload_to)