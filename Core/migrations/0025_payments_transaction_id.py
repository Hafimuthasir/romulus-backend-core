# Generated by Django 4.2.1 on 2023-06-05 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0024_assetlocations_location2_assetlocations_location3'),
    ]

    operations = [
        migrations.AddField(
            model_name='payments',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
