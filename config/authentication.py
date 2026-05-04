"""
Custom authentication classes for Django REST Framework.
"""

from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomBearerAuthentication(JWTAuthentication):
    """
    Custom Bearer token authentication class.
    Extends JWT authentication with additional functionality.
    """
    
    def get_validated_token(self, raw_token):
        """
        Validate the token and return the validated token.
        """
        return super().get_validated_token(raw_token)
    
    def get_user(self, validated_token):
        """
        Get the user from the validated token.
        """
        return super().get_user(validated_token)
