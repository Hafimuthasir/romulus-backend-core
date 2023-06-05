# Generated by Django 4.2.1 on 2023-06-02 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0021_order_diesel_price_order_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='monthly_purchase_cost',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='monthly_purchase_quantity',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='total_outstanding',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='total_purchase_cost',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='company',
            name='total_purchase_quantuty',
            field=models.IntegerField(blank=True, default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(default='ordered', max_length=100),
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(max_length=100)),
                ('payment_price', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('created_month', models.CharField(max_length=100)),
                ('payment_method', models.CharField(blank=True, max_length=100)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
