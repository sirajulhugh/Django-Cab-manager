# Generated by Django 5.1.2 on 2024-11-07 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_alter_trip_trip_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='trip_number',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='guide',
            unique_together={('trip', 'guide_place', 'guide_fee')},
        ),
    ]