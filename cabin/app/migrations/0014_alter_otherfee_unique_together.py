# Generated by Django 5.1.2 on 2024-11-07 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_trip_trip_number_alter_guide_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='otherfee',
            unique_together={('trip', 'value', 'reason')},
        ),
    ]
