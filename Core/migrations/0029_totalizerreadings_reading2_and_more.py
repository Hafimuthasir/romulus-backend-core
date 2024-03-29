# Generated by Django 4.2.3 on 2023-07-21 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0028_alter_romulusassets_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='totalizerreadings',
            name='reading2',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='totalizerreadings',
            name='total_reading',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='totalizerreadings',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Core.romulusassets'),
        ),
    ]
