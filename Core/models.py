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
    role = models.CharField(max_length=30, default='manager')
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



class ClientLocations(models.Model):
    company = models.ForeignKey(User,on_delete=models.CASCADE)
    location = models.TextField(blank=True)    

class Assets(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE)
    assetCapacity = models.IntegerField()
    staff_incharge = models.ForeignKey(User,on_delete=models.CASCADE, related_name='assets_incharge', blank=True,null=True)
    assetLocation = models.ForeignKey(ClientLocations,on_delete=models.CASCADE, blank=True,null=True)
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




class RomulusAssets(models.Model):
    name = models.CharField(max_length=100,unique=True)
    reg_no = models.CharField(max_length=100,null=True,blank=True)
    asset_type = models.CharField(max_length=100)
    assigned_staff = models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True)
    location = models.CharField(max_length=200,null=True,blank=True)
    capacity = models.IntegerField(null=True,blank=True)
    duel_totalizer = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    def delete(self, *args, **kwargs):
        self.is_active = False  
        self.save()



class Order(models.Model):
    company = models.ForeignKey(User,on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='ordered_user')
    requested_quantity = models.IntegerField()
    approved_quantity = models.IntegerField(null=True,blank=True)
    location = models.ForeignKey(ClientLocations,on_delete=models.PROTECT,null=True,blank=True)
    asset = models.ForeignKey(Assets,on_delete=models.PROTECT,null=True,blank=True)
    diesel_price = models.FloatField()
    requested_total_price = models.FloatField()
    order_status = models.CharField(max_length=100,default='Ordered')
    created_at = models.DateTimeField(auto_now_add=True)
    ordered_user_type = models.CharField(max_length=100)
    order_type = models.CharField(max_length=100,default='romulus')
    discount_price = models.FloatField(null=True)
    saved_amount = models.FloatField(null=True)
    by_admin = models.BooleanField(default=False)
    ordered_admin = models.ForeignKey(User,on_delete=models.PROTECT,related_name='ordered_admin',null=True,blank=True)
    order_id = models.CharField(max_length=50, unique=True, editable=False)
    billed = models.BooleanField(default=False)
    is_billable = models.BooleanField(default=False)
    # delivered_by = models.ForeignKey(User,on_delete=models.PROTECT,related_name='delivered_by',null=True,blank=True)
    # delivered_vehicle = models.ForeignKey(RomulusAssets,on_delete=models.PROTECT,null=True,blank=True)
    delivered_quantity = models.FloatField(null=True,blank=True)
    delivered_cost = models.FloatField(null=True,blank=True)

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

    # def get_delivery_price()

class RomulusDeliveries(models.Model):
    def upload_to(instance, filename):
        filename_base, filename_ext = os.path.splitext(filename)
        current_datetime = timezone.now().strftime('%Y_%m_%d_%H_%M_%S')
        unique_id = str(uuid.uuid4().hex[:2])
        return f'Chalans/{current_datetime}_{unique_id}{filename_ext}'
    
    order = models.ForeignKey(Order,on_delete=models.PROTECT ,related_name='deliveries')
    bowser = models.ForeignKey(RomulusAssets,on_delete=models.PROTECT,blank=True)
    quantity = models.FloatField(null=True,blank=True)
    staff_1 = models.ForeignKey(User,on_delete=models.PROTECT)
    staff_2 = models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True,related_name='secondary_staff')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    by_admin = models.BooleanField(default=False)
    chalan_no = models.CharField(null=True,blank=True)
    chalan_image = models.FileField(upload_to=upload_to, null=True, blank=True)
    totalizer = models.IntegerField(null=True,blank=True)
    # totali


class DeliveryTotalizer(models.Model):
    asset = models.ForeignKey(RomulusAssets,on_delete=models.PROTECT)
    delivery = models.OneToOneField(RomulusDeliveries,on_delete=models.PROTECT)



class OrderDistribution(models.Model):
    asset = models.ForeignKey(Assets,on_delete=models.PROTECT)
    quantity = models.FloatField()
    price = models.FloatField(null=True,blank=True)
    created_at = models.DateField(auto_now_add=True)
    delivery = models.ForeignKey(RomulusDeliveries,on_delete=models.PROTECT, related_name='distribution')

    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         tz = pytz.timezone('Asia/Kolkata')
    #         self.created_at = timezone.localtime(timezone.now(), tz)
    #     super().save(*args, **kwargs)
    # payment_status = models.CharField(default=True)
    
    




class TotalizerReadings(models.Model):

    def upload_to(instance, filename):
        filename_base, filename_ext = os.path.splitext(filename)
        current_datetime = timezone.now().strftime('%Y_%m_%d_%H_%M_%S')
        unique_id = str(uuid.uuid4().hex[:2])
        return f'TotalizerReadings/{current_datetime}_{unique_id}{filename_ext}'

    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User,on_delete=models.PROTECT)
    company = models.ForeignKey(User,on_delete=models.PROTECT, related_name='company')
    asset = models.ForeignKey(RomulusAssets,on_delete=models.PROTECT)
    left_reading = models.IntegerField(null=True,blank=True)
    right_reading = models.IntegerField(null=True,blank=True)
    single_reading = models.IntegerField(null=True,blank=True)
    image = models.FileField(upload_to=upload_to)


class Invoice(models.Model):
    def upload_to(instance, filename):
        filename_base, filename_ext = os.path.splitext(filename)
        current_datetime = timezone.now().strftime('%Y_%m_%d_%H_%M_%S')
        unique_id = str(uuid.uuid4().hex[:2])
        return f'Invoices/{current_datetime}_{unique_id}{filename_ext}'
    
    order = models.OneToOneField(Order,on_delete=models.PROTECT)
    invoice_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(User,on_delete=models.PROTECT)
    invoice_no = models.CharField(max_length=255,unique=True)
    dispatch_doc_no = models.CharField(max_length=255,null=True)
    destination = models.CharField(max_length=255)
    amount = models.FloatField()
    paid_amount = models.FloatField(default=0)
    payment_status = models.CharField(max_length=100,default='Pending')
    invoice_file = models.FileField(upload_to=upload_to)

    def get_pending_amount(self):
        if self.payment_status == 'Partial':
            return self.amount - self.paid_amount
        elif self.payment_status == 'Pending':
            return self.amount
        else:
            return 0

class Payment(models.Model):
    company = models.ForeignKey(User,on_delete=models.PROTECT)
    payment_datetime = models.DateTimeField()
    payment_amount = models.FloatField()
    full_payment_invoices = models.ManyToManyField('Invoice',null=True,blank=True, related_name='full_payments')
    partial_payment_invoice = models.ForeignKey(Invoice,null=True,blank=True,on_delete=models.PROTECT)
    partial_amount = models.FloatField(null=True)
    payment_method = models.CharField(max_length=100,)
    transaction_id = models.TextField(null=True,blank=True)
    server_payment_id = models.CharField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk: 
            super().save(*args, **kwargs)

            # prefix = 'PD' if self.payment_type == 'paid' else 'PU'
            formatted_date = timezone.now().strftime("%d%m%y")  
            server_payment_id = f'P{formatted_date}N{self.id}'

            self.server_payment_id = server_payment_id
            self.save(update_fields=['server_payment_id'])
        else:
            super().save(*args, **kwargs)



class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Purchase', 'Purchase'),
        ('Payment', 'Payment'),
    ]

    transaction_date = models.DateField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(User,on_delete=models.PROTECT)
    @property
    def amount(self):
        if self.transaction_type == 'Purchase' and self.invoice:
            return self.invoice.amount
        elif self.transaction_type == 'Payment' and self.payment:
            return self.payment.partial_amount
        return None