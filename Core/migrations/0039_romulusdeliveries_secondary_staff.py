# Generated by Django 4.2.3 on 2023-07-22 11:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0038_romulusdeliveries_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='romulusdeliveries',
            name='secondary_staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='secondary_staff', to=settings.AUTH_USER_MODEL),
        ),
    ]
