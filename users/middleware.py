from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseRedirect

class AuthRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Allow access to admin pages
        if request.path.startswith('/admin') or request.path.startswith('/login'):
            return response

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/login")
        
        return response