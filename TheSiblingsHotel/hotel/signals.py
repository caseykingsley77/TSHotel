from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, Invoice

@receiver(post_save, sender=Booking)
def create_invoice(sender, instance, created, **kwargs):
    if created:
        # Check if an invoice already exists for this booking
        if not hasattr(instance, 'invoice'):
            Invoice.objects.create(booking=instance)
