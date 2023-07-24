# Generated by Django 4.2.3 on 2023-07-20 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0024_order_ordered_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='RomulusAssets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('reg_no', models.CharField(max_length=100)),
                ('asset_type', models.CharField(max_length=100)),
                ('assigned_staff', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
