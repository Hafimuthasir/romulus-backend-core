# Generated by Django 4.2.3 on 2023-07-25 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0049_order_location_alter_orderdistribution_delivery_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
