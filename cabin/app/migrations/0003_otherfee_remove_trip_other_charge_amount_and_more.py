# Generated by Django 5.1.2 on 2024-10-26 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_guide_trip_end_date_trip_guides'),
    ]

    operations = [
        migrations.CreateModel(
            name='Otherfee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, help_text='Fee for the guide', max_digits=10)),
                ('reason', models.CharField(help_text='Place where the guide is required', max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='trip',
            name='other_charge_amount',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='other_charge_description',
        ),
        migrations.AddField(
            model_name='trip',
            name='entrance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
