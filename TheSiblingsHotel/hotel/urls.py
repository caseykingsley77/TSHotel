from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import custom_logout_view

urlpatterns = [
    # Home Page
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('home/', views.home, name='home'),
    path('access-denied/', views.access_denied, name='access_denied'),
    path('register/', views.register, name='register'),
    path('', auth_views.LoginView.as_view(template_name='hotel/registration/login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),

    # Guest Management URLs
    path('guests/create/', views.create_guest, name='create_guest'),
    path('guests/checking-out/', views.guests_checking_out, name='guests_checking_out'),
    path('guests/checkout/<int:guest_id>/<int:invoice_id>/', views.checkout_guest, name='checkout_guest'),
    path('guests/checkout/success/<int:guest_id>/<int:invoice_id>/', views.checkout_success, name='checkout_success'),
    path('guests/extend-stay/success/<int:guest_id>/<int:invoice_id>/', views.extend_success, name='extend_success'),
    path('checking-out/guests/', views.checking_out_guests, name='checking_out_guests'),  # View for guests checking out

    # Room Management URLs
    path('rooms/create/', views.create_room, name='create_room'),
    path('room-types/create/', views.create_room_type, name='create_room_type'),
    path('available-rooms/', views.available_rooms, name='available_rooms'),
    path('assign-room/<int:guest_id>/', views.assign_room, name='assign_room'),

    # Service Management URLs
    path('services/create/', views.create_service, name='create_service'),

    # Booking URLs
    path('booking/create/', views.create_booking, name='create_booking'),
    path('booking/success/', views.booking_success, name='booking_success'),

    # Invoice URLs
    path('invoices/', views.invoices_list, name='invoices_list'),
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),  # Unified invoice view URL

    # Daily Report URLs
    path('report/daily/', views.daily_report, name='daily_report'),

    # AJAX/JSON Endpoints
    path('daily-report-data/', views.daily_report_data, name='daily_report_data'),  # AJAX for daily report data
    path('all-guests-and-bookings/', views.all_guests_and_bookings, name='all_guests_and_bookings'),
    
     # Editing URLs
    path('guest/edit/<int:guest_id>/', views.edit_guest, name='edit_guest'),
    path('room/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('room-type/edit/<int:room_type_id>/', views.edit_room_type, name='edit_room_type'),
    path('service/edit/<int:service_id>/', views.edit_service, name='edit_service'),

    # Deleting URLs
    path('guest/delete/<int:guest_id>/', views.delete_guest, name='delete_guest'),
    path('room/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    path('room-type/delete/<int:room_type_id>/', views.delete_room_type, name='delete_room_type'),
    path('service/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    
    # Admin pages
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/services/', views.admin_service_list, name='admin_service_list'),
    path('admin/services-dashboard/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('admin/services-dashboard/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    
    
    path('admin-dashboard/rooms/', views.admin_room_list, name='admin_room_list'),
    path('admin-dashboard/guests/', views.admin_guest_list, name='admin_guest_list'),
    path('admin-dashboard/services/', views.admin_service_list, name='admin_service_list'),
    path('admin-dashboard/room-types/', views.admin_room_type_list, name='admin_room_type_list'),
    
    path('admin-dashboard/services/', views.admin_service_list, name='admin_service_list'),
    path('admin-dashboard/rooms/', views.admin_room_list, name='admin_room_list'),
    path('admin-dashboard/room-types/', views.admin_room_type_list, name='admin_room_type_list'),
    path('admin-dashboard/guests/', views.admin_guest_list, name='admin_guest_list'),
    
    # Admin URLs for managing each entity
    path('admin-dashboard/guests/', views.admin_guest_list, name='admin_guest_list'),
    path('admin-dashboard/services/', views.admin_service_list, name='admin_service_list'),
    path('admin-dashboard/rooms/', views.admin_room_list, name='admin_room_list'),
    path('admin-dashboard/room-types/', views.admin_room_type_list, name='admin_room_type_list'),

    # Editing Views
    path('admin-dashboard/guests/edit/<int:guest_id>/', views.edit_guest, name='edit_guest'),
    path('admin-dashboard/rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('admin-dashboard/room-types/edit/<int:room_type_id>/', views.edit_room_type, name='edit_room_type'),
    path('admin-dashboard/services/edit/<int:service_id>/', views.edit_service, name='edit_service'),

    # Deleting Views
    path('admin-dashboard/guests/delete/<int:guest_id>/', views.delete_guest, name='delete_guest'),
    path('admin-dashboard/rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
    path('admin-dashboard/room-types/delete/<int:room_type_id>/', views.delete_room_type, name='delete_room_type'),
    path('admin-dashboard/services/delete/<int:service_id>/', views.delete_service, name='delete_service'),

]
