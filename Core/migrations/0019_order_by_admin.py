# Generated by Django 4.2.3 on 2023-07-18 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0018_alter_companyinfo_total_outstanding'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='by_admin',
            field=models.BooleanField(default=False),
        ),
    ]
