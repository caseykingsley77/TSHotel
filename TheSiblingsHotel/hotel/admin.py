from django.contrib import admin
from .models import RoomType, Room, Guest, Booking, Service, Invoice

admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(Guest)
admin.site.register(Booking)
admin.site.register(Service)
admin.site.register(Invoice)
