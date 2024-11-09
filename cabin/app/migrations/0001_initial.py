# Generated by Django 5.1.2 on 2024-10-24 10:04

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Parking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Toll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=150)),
                ('mobile_number', models.CharField(max_length=15, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_number', models.CharField(editable=False, max_length=10, unique=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('vehicle_name', models.CharField(max_length=100)),
                ('vehicle_number', models.CharField(max_length=20)),
                ('fixed_charge', models.DecimalField(decimal_places=2, max_digits=10)),
                ('max_kilometers', models.DecimalField(decimal_places=2, help_text='Maximum kilometers allowed without extra charge.', max_digits=5)),
                ('extra_running_charge', models.DecimalField(decimal_places=2, help_text='Charge for each extra kilometer.', max_digits=5)),
                ('driver_name', models.CharField(max_length=100)),
                ('guest_name', models.CharField(max_length=100)),
                ('starting_km', models.DecimalField(decimal_places=2, help_text='Starting odometer reading.', max_digits=6)),
                ('ending_km', models.DecimalField(decimal_places=2, help_text='Ending odometer reading.', max_digits=6)),
                ('starting_place', models.CharField(max_length=200)),
                ('starting_time', models.TimeField()),
                ('destination_place', models.CharField(max_length=200)),
                ('ending_place', models.CharField(max_length=200)),
                ('ending_time', models.TimeField()),
                ('permit', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('other_charge_description', models.CharField(blank=True, max_length=255, null=True)),
                ('other_charge_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('advance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('parking_fees', models.ManyToManyField(blank=True, related_name='trip_related_parking_fees', to='app.parking')),
                ('tolls', models.ManyToManyField(blank=True, related_name='trip_related_tolls', to='app.toll')),
            ],
        ),
        migrations.CreateModel(
            name='TripFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_name', models.CharField(max_length=100)),
                ('guest_behavior', models.CharField(choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')], default='Good', help_text="Rate the guest's behavior.", max_length=255)),
                ('trip_conditions', models.CharField(choices=[('Smooth', 'Smooth'), ('Some difficulties', 'Some difficulties'), ('Challenging', 'Challenging')], default='Smooth', help_text='How was the overall condition of the trip?', max_length=255)),
                ('route_difficulty', models.CharField(choices=[('Easy', 'Easy'), ('Moderate', 'Moderate'), ('Difficult', 'Difficult')], default='Moderate', help_text='Rate the difficulty of the route.', max_length=255)),
                ('traffic_conditions', models.CharField(choices=[('Clear', 'Clear'), ('Moderate', 'Moderate'), ('Heavy', 'Heavy')], default='Moderate', help_text='How were the traffic conditions during the trip?', max_length=255)),
                ('additional_comments', models.TextField(blank=True, help_text='Any additional comments about the trip.', null=True)),
                ('feedback_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip_feedback', to='app.trip')),
            ],
        ),
    ]