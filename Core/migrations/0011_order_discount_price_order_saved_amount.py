# Generated by Django 4.2.1 on 2023-07-07 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0010_companyinfo_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount_price',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='saved_amount',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
