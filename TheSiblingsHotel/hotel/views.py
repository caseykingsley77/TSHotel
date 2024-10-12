from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Room, Guest, Booking
from datetime import timedelta
from datetime import datetime  # <-- Add this line to import datetime
from django.contrib.auth import logout
from .models import *
from django.http import JsonResponse
from django.db.models import Sum
from .forms import DateRangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.utils import timezone
from django.db.models import F
from django.utils import timezone
from django.shortcuts import render
from collections import defaultdict
from .models import Booking
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import Booking, Invoice
from .forms import DateRangeForm
from django.shortcuts import render, redirect
from .forms import BookingForm
from .models import Room, Guest, Booking
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Room, RoomType, Guest, Service
from .forms import RoomForm, RoomTypeForm, GuestForm, ServiceForm
from django.db import transaction
from django.shortcuts import render
from django.db.models import Q
from collections import defaultdict, OrderedDict
from datetime import datetime
from .models import Booking
from .forms import GuestForm, ServiceForm, RoomForm, RoomTypeForm
from django.shortcuts import render, redirect
from .models import Guest
from .forms import GuestForm

def privacy_policy(request):
    return render(request, 'hotel/privacy_policy.html')


# Custom function to check if a user is an admin
def is_admin_user(user):
    return user.is_authenticated and user.is_superuser

# Utility decorator for admin access redirection
def admin_required(view_func):
    decorated_view_func = login_required(user_passes_test(
        is_admin_user, 
        login_url='access_denied'  # This will redirect to our custom access denied page
    )(view_func))
    return decorated_view_func


@login_required
def home(request):
    vacant_rooms = Room.objects.filter(is_occupied=False)
    return render(request, 'hotel/home.html', {'vacant_rooms': vacant_rooms})


@login_required
def available_rooms(request):
    rooms = Room.objects.filter(is_occupied=False)
    return render(request, 'hotel/available_rooms.html', {'rooms': rooms})


@login_required
def create_booking(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        # Create a guest object and save booking
        guest = Guest.objects.create(
            title=request.POST['title'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            email=request.POST['email'],
            phone_number=request.POST['phone_number'],
            home_address=request.POST['home_address'],
            occupation=request.POST['occupation']
        )
        check_in = timezone.now()
        days_staying = int(request.POST['days_staying'])
        check_out = check_in + timedelta(days=days_staying)
        total_amount = room.room_type.price_per_night * days_staying
        booking = Booking.objects.create(
            room=room,
            guest=guest,
            check_in=check_in,
            check_out=check_out,
            total_amount=total_amount
        )
        room.is_occupied = True
        room.save()
        return redirect('booking_success')

    return render(request, 'hotel/create_booking.html', {'room': room})


@login_required
def checking_out_guests(request):
    today = timezone.now().date()
    # Fetch all bookings that are checking out today and include related guest and room details
    guests = Booking.objects.select_related('guest', 'room').filter(check_out__date=today)
    return render(request, 'hotel/checking_out_guests.html', {'guests': guests})



@login_required
def guests_checking_out(request):
    # Get today's date and time in local timezone
    today = timezone.localtime()
    start_time = timezone.datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=timezone.localtime().tzinfo)
    end_time = start_time + timezone.timedelta(days=7, hours=23, minutes=59, seconds=59)  # Next 7 days window

    # Filter bookings for rooms that are currently occupied and check-out date within the next 7 days,
    # and exclude guests who have already checked out (actual_check_out is not null)
    guests = Booking.objects.filter(
        check_out__range=(start_time, end_time),  # Check-out within the next 7 days
        room__is_occupied=True,  # Room is still occupied
        actual_check_out__isnull=True  # Exclude guests who have already checked out
    ).select_related('guest', 'room').order_by('check_out')

    # Group the guests by checkout date
    guests_by_date = defaultdict(list)
    for booking in guests:
        checkout_date = booking.check_out.date()
        guests_by_date[checkout_date].append(booking)

    # Render template with grouped guests by date
    return render(request, 'hotel/checking_out_guests.html', {'guests_by_date': dict(guests_by_date)})


@login_required
def invoices_list(request):
    now = timezone.now()

    # Filter invoices where the room is occupied and the current date is within the booking period
    occupied_invoices = Invoice.objects.filter(
        booking__check_in__lte=now, 
        booking__check_out__gte=now
    )

    # Filter invoices where the room is not occupied and the booking has ended
    unoccupied_invoices = Invoice.objects.filter(
        booking__check_out__lt=now
    )

    # Ensure each invoice has a calculated total_amount if not already set
    for invoice in occupied_invoices:
        if invoice.total_amount == 0.00:
            invoice.total_amount = invoice.total_cost
            invoice.save()

    for invoice in unoccupied_invoices:
        if invoice.total_amount == 0.00:
            invoice.total_amount = invoice.total_cost
            invoice.save()

    return render(request, 'hotel/invoices_list.html', {
        'occupied_invoices': occupied_invoices,
        'unoccupied_invoices': unoccupied_invoices
    })


@login_required
# View a specific invoice and add services to it
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    services = Service.objects.all()
    
    if request.method == 'POST':
        service_ids = request.POST.getlist('services')
        for service_id in service_ids:
            service = Service.objects.get(id=service_id)
            invoice.services.add(service)
        invoice.total_services_cost += sum([s.price for s in invoice.services.all()])
        invoice.save()
        return redirect('view_invoice', invoice_id=invoice.id)

    return render(request, 'hotel/view_invoice.html', {'invoice': invoice, 'services': services})


@login_required
def guests_list(request):
    guests = Guest.objects.all()
    return render(request, 'hotel/guests_list.html', {'guests': guests})


@login_required
def daily_report(request):
    today = timezone.now().date()

    # Initialize the form with GET parameters if available
    form = DateRangeForm(request.GET or None)
    start_date = form.cleaned_data.get('start_date') if form.is_valid() else None
    end_date = form.cleaned_data.get('end_date') if form.is_valid() else None

    # Default range is the last 7 days if no date range is provided
    if not start_date:
        start_date = today - timedelta(days=7)
    if not end_date:
        end_date = today

    # Fetch bookings within the custom or default date range
    daily_reports = []
    total_income = 0

    current_day = end_date
    while current_day >= start_date:
        # Debugging: Check what bookings are being retrieved
        bookings = Booking.objects.filter(check_in__date=current_day)

        day_total = 0
        booking_details = []

        for booking in bookings:
            # Initialize the room cost and services cost
            room_cost = booking.total_amount
            services_cost = 0
            total_booking_cost = room_cost

            # If the booking has an invoice, use the invoice's details
            if hasattr(booking, 'invoice'):
                invoice = booking.invoice
                services_cost = invoice.total_services_cost
                total_booking_cost = invoice.total_cost  # Calculate the total based on invoice details

                booking_details.append({
                    'guest': booking.guest,
                    'room': booking.room,
                    'check_in': booking.check_in,
                    'check_out': booking.check_out,
                    'room_cost': room_cost,
                    'services_cost': services_cost,
                    'total': total_booking_cost,
                    'invoice_id': invoice.id
                })
            else:
                # If no invoice, use only the room cost
                booking_details.append({
                    'guest': booking.guest,
                    'room': booking.room,
                    'check_in': booking.check_in,
                    'check_out': booking.check_out,
                    'room_cost': room_cost,
                    'services_cost': 0,
                    'total': room_cost,
                    'invoice_id': None
                })

            day_total += total_booking_cost

        # Accumulate the day total to the overall income
        total_income += day_total

        # Append the day's report to the list
        daily_reports.append({
            'day': current_day,
            'bookings': booking_details,
            'day_total': day_total
        })

        # Move to the previous day
        current_day -= timedelta(days=1)


    # Render the report with the calculated data
    return render(request, 'hotel/daily_report.html', {
        'total_income': total_income,
        'daily_reports': daily_reports,
        'form': form
    })
    

@login_required
def daily_report_data(request):
    """
    This function dynamically fetches and returns the daily report data
    based on the provided date range (start_date and end_date) using AJAX.
    """
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Default to today if no date range is provided
    today = timezone.now().date()

    # Parse start_date and end_date if provided, otherwise set default values
    if start_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = today - timedelta(days=7)

    if end_date:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = today

    # Fetch bookings within the date range and calculate daily totals
    daily_reports = []
    total_income = 0
    current_day = end_date

    while current_day >= start_date:
        # Fetch bookings for the specific day
        bookings = Booking.objects.filter(check_in__date=current_day)
        day_total = 0
        booking_details = []

        for booking in bookings:
            # Initialize costs for room and services
            room_cost = booking.total_amount
            services_cost = 0
            total_booking_cost = room_cost

            if hasattr(booking, 'invoice'):
                invoice = booking.invoice
                services_cost = invoice.total_services_cost
                total_booking_cost = invoice.total_cost

            # Add booking details to the daily report
            booking_details.append({
                'guest_name': f"{booking.guest.first_name} {booking.guest.last_name}",
                'room_number': booking.room.room_number,
                'check_in': booking.check_in.strftime('%b %d, %Y %I:%M %p'),
                'check_out': booking.check_out.strftime('%b %d, %Y %I:%M %p'),
                'room_cost': room_cost,
                'services_cost': services_cost,
                'total': total_booking_cost,
                'invoice_id': invoice.id if hasattr(booking, 'invoice') else None,
            })
            day_total += total_booking_cost

        # Append the day's report
        total_income += day_total
        daily_reports.append({
            'day': current_day.strftime('%b %d, %Y'),  # Format the date for display
            'bookings': booking_details,
            'day_total': day_total
        })

        # Move to the previous day
        current_day -= timedelta(days=1)

    # Return the JSON response with total income and daily reports
    return JsonResponse({
        'total_income': total_income,
        'daily_reports': daily_reports
    })


@login_required
@transaction.atomic
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            room = booking.room
            
            if not room.is_occupied:  # Check if room is available
                room.is_occupied = True  # Mark room as occupied
                room.save()

                # Save booking
                booking.save()

                # Automatically create an invoice for the booking
                invoice = Invoice.objects.create(booking=booking)
                
                return redirect('booking_success')
            else:
                form.add_error('room', 'This room is already occupied.')
    else:
        form = BookingForm()

    return render(request, 'hotel/create_booking.html', {'form': form})


@login_required
@transaction.atomic
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            room = booking.room
            if not room.is_occupied:
                room.is_occupied = True
                room.save()
                
                # Save booking
                booking.save()

                # Automatically create an invoice for the booking
                invoice = Invoice.objects.create(booking=booking)
                
                return redirect('booking_success')
    else:
        form = BookingForm()
    return render(request, 'hotel/create_booking.html', {'form': form})
@login_required
def booking_success(request):
    return render(request, 'hotel/booking_success.html')

@login_required
def checkout_guest(request, guest_id, invoice_id):
    guest = get_object_or_404(Guest, id=guest_id)
    invoice = get_object_or_404(Invoice, id=invoice_id)
    booking = invoice.booking

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'confirm_payment':
            # Mark the room as available after guest checks out
            booking.actual_check_out = timezone.now()
            booking.room.is_occupied = False
            booking.room.save()
            booking.save()
            return redirect('checkout_success', guest_id=guest.id, invoice_id=invoice.id)

        elif action == 'extend_stay':
            new_check_out_date_str = request.POST.get('new_check_out')
            
            if new_check_out_date_str:
                # Parse the new check-out date
                new_check_out_date = datetime.strptime(new_check_out_date_str, '%Y-%m-%d').date()

                # Calculate the difference in days between the original and new check-out date
                original_days = (booking.check_out - booking.check_in).days
                new_days = (new_check_out_date - booking.check_in.date()).days

                # Calculate the additional cost for the extended days
                extra_days = new_days - original_days

                if extra_days > 0:
                    # Calculate the additional cost
                    additional_cost = booking.room.room_type.price_per_night * extra_days

                    # Update the booking's check-out date and total amount
                    booking.check_out = timezone.make_aware(datetime.combine(new_check_out_date, timezone.datetime.min.time()))
                    booking.total_amount += additional_cost
                    booking.save()

                    # Update the invoice's total amount
                    invoice.total_amount = invoice.booking.total_amount + invoice.total_services_cost
                    invoice.save()

            return redirect('extend_success', guest_id=guest.id, invoice_id=invoice.id)

    return render(request, 'hotel/checkout_guest.html', {'guest': guest, 'invoice': invoice})
@login_required
def checkout_success(request, guest_id, invoice_id):
    guest = Guest.objects.get(id=guest_id)
    invoice = Invoice.objects.get(id=invoice_id)
    return render(request, 'hotel/checkout_success.html', {'guest': guest, 'invoice': invoice})
@login_required
def extend_success(request, guest_id, invoice_id):
    guest = Guest.objects.get(id=guest_id)
    invoice = Invoice.objects.get(id=invoice_id)
    return render(request, 'hotel/extend_success.html', {'guest': guest, 'invoice': invoice})




@login_required
@admin_required
def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ServiceForm()
    return render(request, 'hotel/create_service.html', {'form': form})


@login_required
@admin_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RoomForm()
    return render(request, 'hotel/create_room.html', {'form': form})


@login_required
@admin_required
def create_room_type(request):
    if request.method == 'POST':
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RoomTypeForm()
    return render(request, 'hotel/create_room_type.html', {'form': form})


@login_required
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    services = Service.objects.all()
    
    if request.method == 'POST':
        service_ids = request.POST.getlist('services')
        for service_id in service_ids:
            service = Service.objects.get(id=service_id)
            # Add the service to the invoice with a quantity of 1 if it's a new service
            invoice_service, created = InvoiceService.objects.get_or_create(invoice=invoice, service=service)
            if not created:
                invoice_service.quantity += 1  # Increment quantity if already exists
            invoice_service.save()

        # Update the total services cost and save the invoice
        invoice.total_services_cost = sum([item.service.price * item.quantity for item in invoice.invoiceservice_set.all()])
        invoice.total_amount = invoice.booking.total_amount + invoice.total_services_cost
        invoice.save()
        return redirect('view_invoice', invoice_id=invoice.id)

    return render(request, 'hotel/view_invoice.html', {'invoice': invoice, 'services': services, 'total_cost': invoice.total_cost})
@login_required
def create_guest(request):
    guests = Guest.objects.all()
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            guest = form.save()
            return redirect('assign_room', guest_id=guest.id)  # Redirect to assign room to guest
    else:
        form = GuestForm()
    return render(request, 'hotel/create_guest.html', {'form': form, 'guests': guests})
@login_required
def assign_room(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    available_rooms = Room.objects.filter(is_occupied=False)

    if request.method == 'POST':
        room_id = request.POST.get('room')
        days_staying = int(request.POST.get('days_staying', 1))
        room = get_object_or_404(Room, id=room_id)

        # Assign room to guest
        room.is_occupied = True
        room.save()

        check_in = timezone.now()
        check_out = check_in + timedelta(days=days_staying)
        total_amount = room.room_type.price_per_night * days_staying

        booking = Booking.objects.create(
            room=room,
            guest=guest,
            check_in=check_in,
            check_out=check_out,
            total_amount=total_amount
        )

        # Check if an invoice already exists for this booking
        if not hasattr(booking, 'invoice'):
            Invoice.objects.create(booking=booking)

        return redirect('view_invoice', invoice_id=booking.invoice.id)

    return render(request, 'hotel/assign_room.html', {'guest': guest, 'available_rooms': available_rooms})
@login_required
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    services = Service.objects.all()

    if request.method == 'POST':
        service_ids = request.POST.getlist('services')
        for service_id in service_ids:
            service = get_object_or_404(Service, id=service_id)

            # Check if this service is already added to the invoice
            invoice_service, created = InvoiceService.objects.get_or_create(invoice=invoice, service=service)
            if not created:
                invoice_service.quantity += 1  # Increment quantity if the service already exists
            invoice_service.save()

        # Recalculate the total_services_cost
        invoice.total_services_cost = sum([item.service.price * item.quantity for item in invoice.invoiceservice_set.all()])
        
        # Recalculate the total_amount (room cost + services cost)
        invoice.total_amount = invoice.booking.total_amount + invoice.total_services_cost
        invoice.save()

        return redirect('view_invoice', invoice_id=invoice.id)

    return render(request, 'hotel/view_invoice.html', {'invoice': invoice, 'services': services})


@login_required
def all_guests_and_bookings(request):
    # Retrieve all bookings, including guests and room details, ordered by check-in date
    bookings = Booking.objects.select_related('guest', 'room').order_by('-check_in')

    # Filter by guest name if specified
    name_filter = request.GET.get('name')
    if name_filter:
        bookings = bookings.filter(
            Q(guest__first_name__icontains=name_filter) |
            Q(guest__last_name__icontains=name_filter) |
            Q(guest__middle_name__icontains=name_filter)
        )

    # Filter by date if specified
    date_filter = request.GET.get('date')
    if date_filter:
        bookings = bookings.filter(check_in__date=date_filter)

    # Group bookings by date
    grouped_bookings = defaultdict(list)
    for booking in bookings:
        grouped_bookings[booking.check_in.date()].append(booking)

    # Convert grouped_bookings to a sorted dictionary in reverse order
    sorted_grouped_bookings = OrderedDict(
        sorted(grouped_bookings.items(), key=lambda item: item[0], reverse=True)
    )

    # Pass grouped bookings and request data to the template
    return render(request, 'hotel/all_guests_and_bookings.html', {
        'grouped_bookings': sorted_grouped_bookings,
        'request': request
    })




# Utility function to check if the user is an admin
def is_admin_user(user):
    return user.is_authenticated and user.is_superuser

# ---- EDITING VIEWS ----

@admin_required
def edit_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        if form.is_valid():
            form.save()
            return redirect('admin_guest_list')  # Redirect to the guest list view after editing
    else:
        form = GuestForm(instance=guest)
    return render(request, 'hotel/edit_guest.html', {'form': form, 'guest': guest})


@admin_required
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('admin_room_list')  # Redirect to the room list view after editing
    else:
        form = RoomForm(instance=room)
    return render(request, 'hotel/edit_room.html', {'form': form, 'room': room})


@admin_required
def edit_room_type(request, room_type_id):
    room_type = get_object_or_404(RoomType, id=room_type_id)
    if request.method == 'POST':
        form = RoomTypeForm(request.POST, instance=room_type)
        if form.is_valid():
            form.save()
            return redirect('admin_room_type_list')  # Redirect to the room type list view after editing
    else:
        form = RoomTypeForm(instance=room_type)
    return render(request, 'hotel/edit_room_type.html', {'form': form, 'room_type': room_type})


@admin_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('admin_service_list')  # Redirect to the service list view after editing
    else:
        form = ServiceForm(instance=service)
    return render(request, 'hotel/edit_service.html', {'form': form, 'service': service})


# ---- DELETING VIEWS ----

@admin_required
def delete_guest(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)
    if request.method == 'POST':
        guest.delete()
        return redirect('admin_guest_list')
    return render(request, 'hotel/delete_confirmation.html', {'object': guest, 'type': 'Guest'})


@admin_required
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        room.delete()
        return redirect('admin_room_list')
    return render(request, 'hotel/delete_confirmation.html', {'object': room, 'type': 'Room'})


@admin_required
def delete_room_type(request, room_type_id):
    room_type = get_object_or_404(RoomType, id=room_type_id)
    if request.method == 'POST':
        room_type.delete()
        return redirect('admin_room_type_list')
    return render(request, 'hotel/delete_confirmation.html', {'object': room_type, 'type': 'Room Type'})


@admin_required  # Ensure only admin users can access this view
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('admin_service_list')  # Redirect to the service list view after saving
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'hotel/edit_service.html', {'form': form, 'service': service})



def is_admin_user(user):
    return user.is_superuser

@login_required
@admin_required
def admin_dashboard(request):
    return render(request, 'hotel/admin_dashboard.html')

# Service Views
@login_required
@admin_required
def admin_service_list(request):
    services = Service.objects.all()
    return render(request, 'hotel/service_list.html', {'services': services})

@login_required
@admin_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('admin_service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'hotel/edit_service.html', {'form': form, 'service': service})

@login_required
@admin_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.delete()
        return redirect('admin_service_list')
    return render(request, 'hotel/confirm_delete.html', {'service': service})


# Utility function to restrict views to admins only
def is_admin(user):
    return user.is_authenticated and user.is_staff

# View for Services List
@login_required
@admin_required
def admin_service_list(request):
    services = Service.objects.all()
    return render(request, 'hotel/service_list.html', {'services': services})

# View for Rooms List
@login_required
@admin_required
def admin_room_list(request):
    rooms = Room.objects.all()
    return render(request, 'hotel/room_list.html', {'rooms': rooms})

# View for Room Types List
@login_required
@admin_required
def admin_room_type_list(request):
    room_types = RoomType.objects.all()
    return render(request, 'hotel/room_type_list.html', {'room_types': room_types})

# View for Guests List
@login_required
@admin_required
def admin_guest_list(request):
    guests = Guest.objects.all()
    return render(request, 'hotel/guest_list.html', {'guests': guests})



# Registration View
@login_required
@admin_required
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')  # Redirect to login page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'hotel/registration/register.html', {'form': form})

# Login View (Django provides this but you can use a custom view as well)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  # Adjust the 'home' to your desired page after login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'hotel/registration/login.html', {'form': form})

def access_denied(request):
    return render(request, 'hotel/access_denied.html')

@login_required
def custom_logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return HttpResponseNotAllowed(['POST'])