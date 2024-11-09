from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Driver, Trip, Toll, Parking, Guide, Otherfee, TripFeedback, Feedback
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import re
import qrcode
from io import BytesIO
import base64
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import IntegrityError
from .models import Trip, Toll, Parking, Guide, Otherfee, Driver

def check_username(request):
    """AJAX view to check if a username already exists."""
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def check_mobile(request):
    """AJAX view to check if a mobile number already exists."""
    mobile_number = request.GET.get('mobile_number', None)
    data = {
        'is_taken': Driver.objects.filter(mobile_number=mobile_number).exists()
    }
    return JsonResponse(data)

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        full_name = request.POST.get('full_name')
        mobile_number = request.POST.get('mobile_number')

        # Validate mobile number (must be exactly 10 digits)
        if not re.fullmatch(r'^\d{10}$', mobile_number):
            messages.error(request, "Mobile number must be exactly 10 digits.")
        
        # Validate password strength
        elif len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%^&*()_+=-]', password):
            messages.error(request, "Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a digit, and a special character.")
        
        # Other validation checks
        elif password != password_confirm:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
        elif Driver.objects.filter(mobile_number=mobile_number).exists():
            messages.error(request, "Mobile number is already registered.")
        else:
            # Create user account
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Create driver profile
            driver = Driver(user=user, full_name=full_name, mobile_number=mobile_number)
            driver.save()

            messages.success(request, "Your account has been created successfully! Please log in.")
            return redirect('login')  # Redirect to login page after successful signup

    return render(request, 'signup.html')

# Login view
def login_view(request): 
    if request.method == 'POST': 
        username = request.POST.get('username') 
        password = request.POST.get('password') 
        user = authenticate(username=username, password=password) 
        if user is not None: 
            login(request, user) 
            try: 
                driver = Driver.objects.get(user=user) 
                full_name = driver.full_name 
            except Driver.DoesNotExist: 
                full_name = username # Fallback to username if no Driver instance found 
            messages.success(request, f"Glad to have you on board, {full_name}!") 
            return redirect('home') # Redirect to home or dashboard after successful login 
        else: 
            messages.error(request, "Invalid username or password.") 
    return render(request, 'login.html')

# Logout view
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')  # Redirect to login page after logout

from datetime import time
@login_required(login_url='login')
def add_trip(request):
    driver_name = ""
    if request.user.is_authenticated:
        try:
            driver = Driver.objects.get(user=request.user)
            driver_name = driver.full_name
        except Driver.DoesNotExist:
            driver_name = "No driver information available"

    if request.method == 'POST':
        trip_id = request.POST.get('trip_id')  # Check if trip_id is provided for overwriting

        # Check if an existing trip is being updated
        trip = None
        if trip_id:
            try:
                trip = Trip.objects.get(id=trip_id, user=request.user)
                # Generate a new trip ID by adding 1 to the current trip_id
                new_trip_id = int(trip_id) + 1
            except Trip.DoesNotExist:
                trip = None  # Fallback if no existing trip is found

        # Gather data from the form
        trip_data = {
            "trip_number": request.POST.get('trip_number'),
            "vehicle_name": request.POST.get('vehicle_name'),
            "vehicle_number": request.POST.get('vehicle_number'),
            "date": request.POST.get('date', timezone.now().date()),
            "guest_name": request.POST.get('guest_name'),
            "driver_name": request.POST.get('driver_name'),
            "starting_km": request.POST.get('starting_km'),
            "ending_km": request.POST.get('ending_km'),
            "starting_place": request.POST.get('starting_place'),
            "ending_place": request.POST.get('ending_place'),
            "fixed_charge": request.POST.get('fixed_charge'),
            "max_kilometers": request.POST.get('max_kilometers'),
            "extra_running_charge": request.POST.get('extra_running_charge'),
            "advance": request.POST.get('advance', 0),
            "permit": request.POST.get('permit', 0),
            "entrance": request.POST.get('entrance', 0),
            "user": request.user
        }

        # Include end_date in trip_data only if it's provided
        end_date = request.POST.get('end_date')
        if end_date:
            trip_data["end_date"] = end_date

        starting_time = request.POST.get('starting_time')
        if starting_time:
            trip_data["starting_time"] = starting_time

        ending_time = request.POST.get('ending_time')
        if ending_time:
            trip_data["ending_time"] = ending_time

        # Create or update trip
        if trip:
            # Save new trip with the new trip_id
            new_trip = Trip(id=new_trip_id, **trip_data)
            new_trip.save()

            # Delete the original trip entry
            trip.delete()
        else:
            # Create new trip normally if no trip_id is provided
            new_trip = Trip.objects.create(**trip_data)

        # Handle dynamic tolls and associate with the trip, avoiding duplicates
        toll_amounts = request.POST.getlist('toll_amount[]')
        for i, amount in enumerate(toll_amounts):
            if amount and float(amount) > 0:  # Ensure amount is provided and greater than zero
                toll_instance = Toll.objects.filter(trip=new_trip).first() if i == 0 else Toll.objects.filter(trip=new_trip, amount=amount).first()
                
                if toll_instance:
                    # Update if a record exists
                    toll_instance.amount = amount
                    toll_instance.save()
                else:
                    # Create new if no existing record found
                    Toll.objects.create(amount=amount, trip=new_trip)

        # Handle dynamic parking fees and associate with the trip, avoiding duplicates
        parking_amounts = request.POST.getlist('parking_amount[]')
        for i, amount in enumerate(parking_amounts):
            if amount and float(amount) > 0:  # Ensure amount is provided and greater than zero
                parking_instance = Parking.objects.filter(trip=new_trip).first() if i == 0 else Parking.objects.filter(trip=new_trip, amount=amount).first()
                
                if parking_instance:
                    # Update if a record exists
                    parking_instance.amount = amount
                    parking_instance.save()
                else:
                    # Create new if no existing record found
                    Parking.objects.create(amount=amount, trip=new_trip)


        # Handle dynamic guides and associate with the trip, avoiding duplicates
        guide_places = request.POST.getlist('guide_place[]')
        guide_fees = request.POST.getlist('guide_fee[]')
        for place, fee in zip(guide_places, guide_fees):
            if place and fee:
                guide_instance = Guide.objects.filter(trip=new_trip).first() if guide_places.index(place) == 0 else Guide.objects.filter(trip=new_trip, guide_place=place, guide_fee=fee).first()
                
                if guide_instance:
                    # Update if a record exists
                    guide_instance.guide_place = place
                    guide_instance.guide_fee = fee
                    guide_instance.save()
                else:
                    # Create new if no existing record found
                    Guide.objects.create(guide_place=place, guide_fee=fee, trip=new_trip)

        # Handle other fees and associate with the trip, avoiding duplicates
        reasons = request.POST.getlist('reason[]')
        values = request.POST.getlist('value[]')
        for reason, value in zip(reasons, values):
            if reason and value:
                otherfee_instance = Otherfee.objects.filter(trip=new_trip).first() if reasons.index(reason) == 0 else Otherfee.objects.filter(trip=new_trip, reason=reason, value=value).first()
                
                if otherfee_instance:
                    # Update if a record exists
                    otherfee_instance.reason = reason
                    otherfee_instance.value = value
                    otherfee_instance.save()
                else:
                    # Create new if no existing record found
                    Otherfee.objects.create(reason=reason, value=value, trip=new_trip)

        return redirect('trip_list')  # Redirect to a trip list page after saving

    return render(request, 'add_trip.html', {'driver_name': driver_name})






def generate_trip_number(request):
    # Get the logged-in user
    user = request.user
    
    # Fetch the last trip for the logged-in user specifically
    last_trip = Trip.objects.filter(user=user).order_by('id').last()
    
    if last_trip:
        # Extract the number portion from the last trip's trip_number
        last_trip_number = int(last_trip.trip_number.replace('TRP', ''))
        new_trip_number = f'TRP{last_trip_number + 1}'
    else:
        # Set the initial trip number for this user if no previous trips exist
        new_trip_number = 'TRP1'

    # Return the generated trip number as a JSON response
    return JsonResponse({'trip_number': new_trip_number})




@login_required(login_url='login')
def get_last_ride(request):
    if request.user.is_authenticated:
        last_trip = Trip.objects.filter(user=request.user).order_by('-id').first()
        try:
            driver = Driver.objects.get(user=request.user)
            driver_name = driver.full_name
        except Driver.DoesNotExist:
            driver_name = "No driver information available"
        
        if last_trip:
            # Filter out duplicate guide entries
            guides = list(last_trip.guides.values('guide_place', 'guide_fee'))
            unique_guides = []
            seen_guides = set()
            for guide in guides:
                guide_tuple = (guide['guide_place'], guide['guide_fee'])
                if guide_tuple not in seen_guides:
                    seen_guides.add(guide_tuple)
                    unique_guides.append(guide)

            # Filter out duplicate other fee entries
            other_fees = list(last_trip.other_fees.values('reason', 'value'))
            unique_other_fees = []
            seen_other_fees = set()
            for fee in other_fees:
                fee_tuple = (fee['reason'], fee['value'])
                if fee_tuple not in seen_other_fees:
                    seen_other_fees.add(fee_tuple)
                    unique_other_fees.append(fee)

            # Filter out duplicate toll entries
            tolls = list(last_trip.tolls.values('amount'))
            unique_tolls = []
            seen_tolls = set()
            for toll in tolls:
                toll_amount = toll['amount']
                if toll_amount not in seen_tolls:
                    seen_tolls.add(toll_amount)
                    unique_tolls.append(toll)

            # Filter out duplicate parking entries
            parking_fees = list(last_trip.parking_fees.values('amount'))
            unique_parking_fees = []
            seen_parking_fees = set()
            for parking in parking_fees:
                parking_amount = parking['amount']
                if parking_amount not in seen_parking_fees:
                    seen_parking_fees.add(parking_amount)
                    unique_parking_fees.append(parking)

            # Prepare the response data
            data = {
                'success': True,
                'guides': unique_guides,
                'driver_name': driver_name,
                'other_fees': unique_other_fees,
                'tolls': unique_tolls,
                'parking_fees': unique_parking_fees,
                'trip_id': last_trip.id,  # Send the trip ID
                'trip_number': last_trip.trip_number,  # Add trip number
                'vehicle_name': last_trip.vehicle_name,
                'vehicle_number': last_trip.vehicle_number,
                'guest_name': last_trip.guest_name,
                'starting_place': last_trip.starting_place,
                'ending_place': last_trip.ending_place,
                'starting_km': last_trip.starting_km,
                'ending_km': last_trip.ending_km,
                'starting_time': last_trip.starting_time,
                'ending_time': last_trip.ending_time,
                'date': last_trip.date,
                'end_date': last_trip.end_date,
                'fixed_charge': last_trip.fixed_charge,
                'max_kilometers': last_trip.max_kilometers,
                'extra_running_charge': last_trip.extra_running_charge,
                'permit': last_trip.permit,
                'entrance': last_trip.entrance,
                'advance': last_trip.advance,
            }
        else:
            data = {'success': False, 'message': 'No last ride found for this user.'}
    else:
        data = {'success': False, 'error': 'User not authenticated'}
    
    return JsonResponse(data)




@login_required(login_url='login')
def trip_list(request):
    if request.user.is_authenticated:
        # Filter trips associated with the logged-in user
        trips = Trip.objects.filter(user=request.user)
    else:
        trips = Trip.objects.none()  # Return an empty queryset if not authenticated

    return render(request, 'trip_list.html', {'trips': trips})

@login_required(login_url='login')
def trip_view(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    guides = trip.guides.all()
    other_fees = trip.other_fees.all()

    # QR Code generation using trip_id
    
    qr_data = f"https://testproject.infoxtechnologies.com/feedback/{trip.id}"
    qr = qrcode.make(qr_data)
    qr_image = BytesIO()
    qr.save(qr_image, format="PNG")
    qr_image.seek(0)  # Go to the beginning of the BytesIO buffer
    qr_image_base64 = qr_image.getvalue()  # Get the image content in bytes

    return render(request, 'trip_view.html', {
        'trip': trip,
        'guides': guides,
        'other_fees': other_fees,
        'qr_code_image': qr_image_base64
    })

@login_required(login_url='login')
def delete_trip(request, pk):
    if request.method == "POST":
        trip = get_object_or_404(Trip, pk=pk)
        trip.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def feedback_page(request):
    trips = Trip.objects.all()
    
    if request.method == 'POST':
        trip_id = request.POST.get('trip')
        driver_name = request.POST.get('driver_name')
        guest_behavior = request.POST.get('guest_behavior')
        trip_conditions = request.POST.get('trip_conditions')
        route_difficulty = request.POST.get('route_difficulty')
        traffic_conditions = request.POST.get('traffic_conditions')
        additional_comments = request.POST.get('additional_comments')

        # Create and save feedback entry
        feedback = TripFeedback.objects.create(
            trip_id=trip_id,
            driver_name=driver_name,
            guest_behavior=guest_behavior,
            trip_conditions=trip_conditions,
            route_difficulty=route_difficulty,
            traffic_conditions=traffic_conditions,
            additional_comments=additional_comments,
            feedback_date=timezone.now()
        )
        return redirect('home')

    return render(request, 'feedback_page.html', {'trips': trips})

def get_trip_driver(request, trip_id):
    trip = get_object_or_404(Trip, pk=trip_id)
    return JsonResponse({'driver_name': trip.driver_name})

@login_required(login_url='login')
def feedback_list(request):
    driver_feedbacks = Feedback.objects.filter(driver=request.user)
    return render(request, 'feedback_list.html', {'feedbacks': driver_feedbacks})

@login_required(login_url='login')
def feedback_detail(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id, driver=request.user)
    return render(request, 'feedback_detail.html', {'feedback': feedback})

@login_required(login_url='login')
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id, driver=request.user)
    if request.method == 'POST':
        feedback.delete()
        return redirect('feedback_list')
    return render(request, 'confirm_delete.html', {'feedback': feedback})


def feedback_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    
    # Check if feedback already exists for this trip
    if Feedback.objects.filter(trip=trip).exists():
        return HttpResponse("Feedback has already been submitted for this trip.")
    
    if request.method == "POST":
        # Handle form submission
        Feedback.objects.create(
            trip=trip,
            driver=trip.user,
            rating=request.POST.get('rating'),
            comments=request.POST.get('comments'),
        )
        return HttpResponse("Thank you for your feedback!")
    
    return render(request, 'feedback_form.html', {'trip': trip})

