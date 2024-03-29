# Generated by Django 4.2.3 on 2023-07-29 06:48

import Core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0058_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='invoice_image',
            field=models.FileField(default=1, upload_to=Core.models.Invoice.upload_to),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='invoice',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='dispatch_doc_no',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='paid_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_status',
            field=models.CharField(default='Pending', max_length=100),
        ),
    ]
