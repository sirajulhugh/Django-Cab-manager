# Generated by Django 5.1.2 on 2024-11-02 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_feedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='trip_number',
            field=models.CharField(editable=False, max_length=10),
        ),
    ]