# Generated by Django 5.1.2 on 2024-10-29 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_guide_guide_fee_alter_otherfee_reason_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trip',
            name='guides',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='parking_fees',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='tolls',
        ),
        migrations.AddField(
            model_name='guide',
            name='trip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guides', to='app.trip'),
        ),
        migrations.AddField(
            model_name='otherfee',
            name='trip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='other_fees', to='app.trip'),
        ),
        migrations.AddField(
            model_name='parking',
            name='trip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parking_fees', to='app.trip'),
        ),
        migrations.AddField(
            model_name='toll',
            name='trip',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tolls', to='app.trip'),
        ),
    ]
