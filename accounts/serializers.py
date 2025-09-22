# 1. Create accounts/serializers.py
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

class CustomRegisterSerializer(RegisterSerializer):
    password2 = None  # Remove password2 field completely
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password2 field if it exists
        if 'password2' in self.fields:
            del self.fields['password2']
    
    def custom_signup(self, request, user):
        """Override to handle any custom user creation logic"""
        pass
    
    def get_cleaned_data(self):
        """Override to only return the fields we want"""
        return {
            'username': self.validated_data.get('username', ''),
            'email': self.validated_data.get('email', ''),
            'password1': self.validated_data.get('password1', ''),
        }
