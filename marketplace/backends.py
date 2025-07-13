from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class PhoneNumberBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate with phone numbers
    """
    
    def authenticate(self, request, phone=None, password=None, **kwargs):
        if phone is None or password is None:
            return None
        
        try:
            # Try to find user by phone number
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 