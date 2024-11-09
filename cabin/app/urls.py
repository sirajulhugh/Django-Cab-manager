from django.urls import path
from .import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home', views.home, name='home'),  # Change 'home' to your homepage or dashboard view
    path('ajax/check_username/', views.check_username, name='check_username'),  # AJAX for username
    path('ajax/check_mobile/', views.check_mobile, name='check_mobile'),  # AJAX for mobile number
    path('add-trip/', views.add_trip, name='add_trip'),
    path('generate-trip-number/', views.generate_trip_number, name='generate_trip_number'),
    path('get_last_ride/', views.get_last_ride, name='get_last_ride'),
    path('trips/', views.trip_list, name='trip_list'),
    path('trips/<int:pk>/', views.trip_view, name='trip_view'),
    path('trips/<int:pk>/delete/', views.delete_trip, name='delete_trip'),
    path('feedback/', views.feedback_page, name='feedback_page'),
    path('get-trip-driver/<int:trip_id>/', views.get_trip_driver, name='get_trip_driver'),
    path('feedback/<int:trip_id>/', views.feedback_view, name='feedback_form'),
    path('feedbacks/', views.feedback_list, name='feedback_list'),
    path('feedbacks/<int:feedback_id>/', views.feedback_detail, name='feedback_detail'),
    path('feedbacks/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),

]