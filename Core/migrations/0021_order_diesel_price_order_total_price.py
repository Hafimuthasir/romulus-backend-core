# Generated by Django 4.2.1 on 2023-05-31 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0020_order_asset_order_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='diesel_price',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
