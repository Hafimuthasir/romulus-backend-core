# Generated by Django 4.2.3 on 2023-07-27 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0056_romulusdeliveries_chalan_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryTotalizer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Core.romulusassets')),
                ('delivery', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='Core.romulusdeliveries')),
            ],
        ),
    ]