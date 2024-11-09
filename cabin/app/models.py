from django.db import models
from django.utils import timezone

class Trip(models.Model):
    trip_number = models.CharField(max_length=10)
    date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    vehicle_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20)
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2)
    max_kilometers = models.DecimalField(max_digits=5, decimal_places=2, help_text="Maximum kilometers allowed without extra charge.")
    extra_running_charge = models.DecimalField(max_digits=5, decimal_places=2, help_text="Charge for each extra kilometer.")
    driver_name = models.CharField(max_length=100)
    guest_name = models.CharField(max_length=100)
    starting_km = models.DecimalField(max_digits=6, decimal_places=2, help_text="Starting odometer reading.")
    ending_km = models.DecimalField(max_digits=6, decimal_places=2, help_text="Ending odometer reading.")
    starting_place = models.CharField(max_length=200)
    starting_time = models.TimeField(null=True, blank=True)
    ending_place = models.CharField(max_length=200)
    ending_time = models.TimeField(null=True, blank=True)
    
    permit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    entrance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    advance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='user_trips', null=True)

    @property
    def min_charge(self):
        # Check if ending_km is greater than zero
        if self.ending_km > 0:
            distance_covered = self.ending_km - self.starting_km
            if distance_covered >= self.max_kilometers:
                return self.fixed_charge * self.max_kilometers
            else:
                return self.fixed_charge * distance_covered
        else:
            # Return 0 or None if ending_km is not greater than zero
            return 0

        

    @property
    def total_distance(self):
        # Return 0 if ending_km is 0
        return self.ending_km - self.starting_km if self.ending_km > 0 else 0

    @property
    def extra_kilometers(self):
        extra_kms = self.total_distance - self.max_kilometers
        return extra_kms if extra_kms > 0 else 0

    @property
    def extra_charge(self):
        return self.extra_kilometers * self.extra_running_charge

    @property
    def total_toll(self):
        return sum(toll.amount for toll in Toll.objects.filter(trip=self))

    @property
    def total_parking(self):
        return sum(parking.amount for parking in Parking.objects.filter(trip=self))

    @property
    def total_guide_fee(self):
        return sum(guide.guide_fee for guide in Guide.objects.filter(trip=self))

    @property
    def other_charge_amount(self):
        return sum(fee.value for fee in Otherfee.objects.filter(trip=self))

    @property
    def total_charge(self):
        # Return 0 if ending_km is 0
        if self.ending_km == 0:
            return 0
        return (
            self.min_charge +
            self.extra_charge +
            self.permit +
            self.entrance +
            self.total_toll +
            self.total_parking +
            self.other_charge_amount +
            self.total_guide_fee
        )

    @property
    def balance(self):
        return self.total_charge - self.advance

    @property
    def trip_days(self):
        start_datetime = timezone.datetime.combine(self.date, self.starting_time)
        end_datetime = timezone.datetime.combine(self.end_date, self.ending_time)
        days_difference = (end_datetime - start_datetime).days
        return days_difference + 1 if days_difference >= 0 else 1

    def __str__(self):
        return f"{self.trip_number} - {self.driver_name}"

    def save(self, *args, **kwargs):
        if not self.trip_number:
            last_trip = Trip.objects.all().order_by('id').last()
            if last_trip:
                last_trip_number = int(last_trip.trip_number.replace('TRP', ''))
                new_trip_number = last_trip_number + 1
            else:
                new_trip_number = 1
            self.trip_number = f'TRP{new_trip_number}'
        super(Trip, self).save(*args, **kwargs)





class Toll(models.Model):
    trip = models.ForeignKey('Trip', related_name='tolls', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.0)

    def __str__(self):
        return f"Toll - Amount: {self.amount}"
    
    class Meta:
        unique_together = ('trip', 'amount')


class Parking(models.Model):
    trip = models.ForeignKey(Trip, related_name='parking_fees', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.0)

    def __str__(self):
        return f"Parking - Amount: {self.amount}"
    
    class Meta:
        unique_together = ('trip', 'amount')


class Guide(models.Model):
    trip = models.ForeignKey(Trip, related_name='guides', on_delete=models.CASCADE, null=True, blank=True)
    guide_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.0, help_text="Fee for the guide")
    guide_place = models.CharField(max_length=200, blank=True, null=True, help_text="Place where the guide is required")

    def __str__(self):
        return f"Guide at {self.guide_place} - Fee: {self.guide_fee}"

    class Meta:
        unique_together = ('trip', 'guide_place', 'guide_fee')



class Otherfee(models.Model):
    trip = models.ForeignKey(Trip, related_name='other_fees', on_delete=models.CASCADE, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0.0, help_text="Fee for the other charge")
    reason = models.CharField(max_length=200, blank=True, null=True, help_text="Description of the other charge")

    def __str__(self):
        return f"{self.reason} - Fee: {self.value}"
    
    class Meta:
        unique_together = ('trip', 'value', 'reason')



# Extending the User model for drivers
class Driver(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Linking to Django's auth system
    full_name = models.CharField(max_length=150)
    mobile_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.full_name
    
class TripFeedback(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='trip_feedback')
    driver_name = models.CharField(max_length=100)
    
    # Feedback fields related to the driver's experience
    guest_behavior = models.CharField(
        max_length=255, 
        choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Average', 'Average'), ('Poor', 'Poor')],
        default='Good',
        help_text="Rate the guest's behavior."
    )
    trip_conditions = models.CharField(
        max_length=255, 
        choices=[('Smooth', 'Smooth'), ('Some difficulties', 'Some difficulties'), ('Challenging', 'Challenging')],
        default='Smooth',
        help_text="How was the overall condition of the trip?"
    )
    route_difficulty = models.CharField(
        max_length=255, 
        choices=[('Easy', 'Easy'), ('Moderate', 'Moderate'), ('Difficult', 'Difficult')],
        default='Moderate',
        help_text="Rate the difficulty of the route."
    )
    traffic_conditions = models.CharField(
        max_length=255, 
        choices=[('Clear', 'Clear'), ('Moderate', 'Moderate'), ('Heavy', 'Heavy')],
        default='Moderate',
        help_text="How were the traffic conditions during the trip?"
    )
    
    additional_comments = models.TextField(blank=True, null=True, help_text="Any additional comments about the trip.")
    feedback_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Trip Feedback for Trip {self.trip.trip_number} by {self.driver_name}"


class Feedback(models.Model):
    trip = models.OneToOneField('Trip', on_delete=models.CASCADE, related_name='feedback')
    driver = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='driver_feedback')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    comments = models.TextField(blank=True, null=True)
    feedback_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.trip.trip_number}"