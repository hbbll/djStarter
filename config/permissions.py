"""
Custom permissions for the Django REST Framework.
"""

from rest_framework.permissions import BasePermission


class HasUserPermission(BasePermission):
    """
    Custom permission to check if user has specific permissions.
    """
    
    def has_permission(self, request, view):
        """
        Check if the user has the required permission.
        """
        # For now, just check if user is authenticated
        # You can extend this with more sophisticated permission logic
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has permission for the specific object.
        """
        # For now, just check if user is authenticated
        # You can extend this with object-level permission logic
        return request.user and request.user.is_authenticated
