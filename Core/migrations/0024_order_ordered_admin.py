# Generated by Django 4.2.3 on 2023-07-20 07:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0023_remove_order_ordered_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ordered_admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ordered_admin', to=settings.AUTH_USER_MODEL),
        ),
    ]
