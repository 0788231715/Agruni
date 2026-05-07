from django.utils import timezone
from accounts.models import User

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last_seen timestamp
            User.objects.filter(pk=request.user.pk).update(last_seen=timezone.now())
        
        response = self.get_response(request)
        return response
