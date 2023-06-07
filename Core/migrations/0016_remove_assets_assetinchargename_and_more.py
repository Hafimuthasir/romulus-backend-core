# Generated by Django 4.2.1 on 2023-05-30 08:14

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0015_alter_company_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assets',
            name='assetInchargeName',
        ),
        migrations.RemoveField(
            model_name='assets',
            name='assetInchargeNumber',
        ),
        migrations.AddField(
            model_name='assets',
            name='staffs_incharge',
            field=models.ManyToManyField(blank=True, related_name='assets_incharge', to=settings.AUTH_USER_MODEL),
        ),
    ]