# Generated by Django 4.2.3 on 2023-07-31 09:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0067_payment_server_payment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
