# Generated by Django 4.2.1 on 2023-05-29 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0008_alter_assets_fueltype'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='user_type',
            field=models.CharField(default='manager', max_length=10),
        ),
    ]