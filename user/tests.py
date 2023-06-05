from django.test import TestCase
from django.test import TestCase
from django.utils import timezone
from Core.models import Order, Company, Assets



class OrderModelTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(username='Company A')
        self.asset = Assets.objects.create(company=self.company, assetName='Asset 1', assetCapacity=500, assetPincode=123)

    def test_create_orders(self):
        for i in range(50):
            order = Order.objects.create(
                company=self.company,
                ordered_by=self.company,
                quantity=10,
                asset=self.asset,
                diesel_price=3.5,
                total_price=35.0,
                order_status='ordered',
                created_at=timezone.now(),
                ordered_user_type='manager'
            )

        self.assertEqual(Order.objects.count(), 50)
