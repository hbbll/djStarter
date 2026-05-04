from rest_framework.response import Response
from config.views import BasePermissionModelViewSet
from config.pagination import PageNumberPagination
from apps.account.api.serializers import PermissionSerializer, PermissionGroupSerializer
from apps.account.models import Permission, PermissionGroup


class PermissionViewSet(BasePermissionModelViewSet):
    required_permissions = {
        "list": ["manage_role"],
        "retrieve": ["manage_role"],
    }

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = PageNumberPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PermissionGroupViewSet(BasePermissionModelViewSet):
    required_permissions = {
        "list": ["manage_permission_group"],
        "retrieve": ["manage_permission_group"],
    }

    queryset = PermissionGroup.objects.all()
    serializer_class = PermissionGroupSerializer
    pagination_class = PageNumberPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
