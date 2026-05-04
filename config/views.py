"""
Base view classes for the Django REST Framework.
"""

from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated


class BasePermissionModelViewSet(viewsets.ModelViewSet):
    """
    Base ModelViewSet with permission handling.
    """
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Get the queryset for this view.
        Override this method in subclasses.
        """
        return super().get_queryset()
