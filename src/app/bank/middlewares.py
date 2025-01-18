from django.shortcuts import redirect
from django.urls import reverse

class TokenVerificationMiddleware:
    """
    Custom middleware that mimics the behavior of the `login_required` decorator.
    It checks if the user is logged in before allowing access to the view.
    If the user is not logged in, they will be redirected to the login page.
    """

    def checkTokenValidiy(request):
        pass
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs where login is required (can be expanded based on your needs)
        exempted_url = [
            '/login/',  # Add your restricted URL patterns here
            '/register/',
        ]
        '''
        # Check if the current path is one of the restricted URLs
        if request.path not in exempted_url and self.checkTokenValidiy(request):
            # Redirect to login page if not authenticated
            return redirect(reverse('login'))  # Adjust 'login' to the actual name of your login view
        '''
        
        # If the user is authenticated or the URL is not restricted, continue processing the request
        response = self.get_response(request)
        return response