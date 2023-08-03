# Generated by Django 4.2.3 on 2023-07-27 09:43

import Core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0055_remove_order_delivered_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='romulusdeliveries',
            name='chalan_image',
            field=models.FileField(blank=True, null=True, upload_to=Core.models.RomulusDeliveries.upload_to),
        ),
        migrations.AddField(
            model_name='romulusdeliveries',
            name='chalan_no',
            field=models.CharField(blank=True, null=True),
        ),
    ]
