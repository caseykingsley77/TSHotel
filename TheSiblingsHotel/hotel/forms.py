from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = [
            'title', 'first_name', 'middle_name', 'last_name', 'email',
            'phone_number', 'home_address', 'occupation', 'valid_id', 
            'passport_number', 'next_of_kin_phone_number', 'car_plate_number'
        ]
        widgets = {
            'title': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'placeholder': 'Enter guest email (optional)', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'home_address': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'valid_id': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'car_plate_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'is_occupied']

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'price_per_night']
        
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'guest', 'check_in', 'check_out', 'total_amount']

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError("Check-out date must be after the check-in date.")

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                room=room,
                check_in__lte=check_out,
                check_out__gte=check_in
            ).exclude(id=self.instance.id if self.instance else None)

            if overlapping_bookings.exists():
                raise forms.ValidationError("This room is already booked for the selected dates.")

        return cleaned_data
    

# New DateRangeForm for Daily Report Filtering
class DateRangeForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))






class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
