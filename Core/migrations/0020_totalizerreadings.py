# Generated by Django 4.2.3 on 2023-07-19 07:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0019_order_by_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='TotalizerReadings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('reading', models.IntegerField()),
                ('image', models.FileField(upload_to='./TotalizerReadings')),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Core.assets')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='company', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
