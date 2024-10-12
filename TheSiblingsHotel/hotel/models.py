from django.db import models, IntegrityError
from django.utils import timezone
from datetime import timedelta

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Room(models.Model):
    room_number = models.CharField(max_length=10)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.room_type.name} - {self.room_number}"


class Guest(models.Model):
    title = models.CharField(max_length=10, choices=[('Mr', 'Mr', ), ('Mrs', 'Mrs'), ('Miss', 'Miss')], blank=True, null=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)  # New field for middle name
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=255, blank=True, null=True)  # Change to CharField to allow plain text
    phone_number = models.CharField(max_length=15)
    home_address = models.CharField(max_length=500)
    occupation = models.CharField(max_length=500)
    valid_id = models.BooleanField(default=False, blank=True, null=True)  # New boolean field for ID verification
    passport_number = models.CharField(max_length=50, blank=True, null=True)  # New field for passport number if the guest is a foreigner
    next_of_kin_phone_number = models.CharField(max_length=15, blank=True, null=True)  # New field for next of kin phone number
    car_plate_number = models.CharField(max_length=50, blank=True, null=True)  # New field for car plate number

    def __str__(self):
        return f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip()


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    actual_check_out = models.DateTimeField(blank=True, null=True)  # Track actual checkout time
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # If this is a new booking, create an invoice if none exists
        if is_new and not hasattr(self, 'invoice'):
            try:
                Invoice.objects.create(booking=self)
            except IntegrityError:
                print(f"Invoice already exists for Booking {self.pk}")

    def check_out_guest(self):
        # Mark the guest as checked out
        self.actual_check_out = timezone.now()
        self.room.is_occupied = False  # Mark room as no longer occupied
        self.room.save()
        self.save()

    def __str__(self):
        return f"Booking {self.id} - {self.guest}"

    
    
class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


from django.db import models, transaction
from django.utils import timezone

class Invoice(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE)
    services = models.ManyToManyField('Service', blank=True, through='InvoiceService')
    invoice_number = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Unique Invoice Number
    total_services_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    invoice_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Use a database transaction to ensure atomicity
        with transaction.atomic():
            if not self.invoice_number:
                # Get or create the InvoiceNumber object and update the number atomically
                invoice_number_obj, created = InvoiceNumber.objects.select_for_update().get_or_create(pk=1)

                # Increment the last number
                invoice_number_obj.last_number += 1
                invoice_number_obj.save()

                # Assign the new invoice number
                self.invoice_number = f"INV-{invoice_number_obj.last_number:05d}"
            
            # Save the invoice with the generated or existing invoice number
            super().save(*args, **kwargs)

    @property
    def total_cost(self):
        # Recalculate the total cost including services
        total_services_cost = sum([item.service.price * item.quantity for item in self.invoiceservice_set.all()])
        return self.booking.total_amount + total_services_cost

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.booking.guest}"


class InvoiceService(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Track quantity of each service

    def __str__(self):
        return f"{self.service.name} (x{self.quantity}) for Invoice {self.invoice.id}"


class InvoiceNumber(models.Model):
    last_number = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Last Invoice Number: {self.last_number}"