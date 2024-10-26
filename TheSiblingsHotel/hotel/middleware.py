# middleware.py

from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseForbidden


class LoginRequiredMiddleware:
    """
    Middleware that redirects users to the login page if they try to access
    any view that requires authentication but are not logged in.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the URL of the current request
        path = request.path_info

        # If the user is not authenticated and trying to access a restricted page
        if not request.user.is_authenticated and not path.startswith(reverse('login')):
            return redirect(f'{settings.LOGIN_URL}?next={request.path}')
        
        # Otherwise, continue processing the request
        response = self.get_response(request)
        return response
    
    
# ALLOWED_IPS = [
#         '127.0.0.1',     # Allow localhost (for testing)
#         '192.168.1.100', # Replace with your allowed IPs
#         '203.0.113.50',  # Example of an external IP address
#     ]


class RestrictIPMiddleware:
    

    """
    Middleware that restricts access to specific IP addresses.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = ALLOWED_IPS

    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        if client_ip not in self.allowed_ips:
            return HttpResponseForbidden("Access Denied: Your IP is not allowed.")
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        """Utility to get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
