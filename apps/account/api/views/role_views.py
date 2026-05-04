from rest_framework.response import Response
from config.views import BasePermissionModelViewSet
from config.pagination import PageNumberPagination
from apps.account.api.serializers import *
from apps.account.models import *
from apps.account.api.service import RoleService


class RoleViewSet(BasePermissionModelViewSet):
    required_permissions = {
        "list": ["user_view", "view_role"],
        "retrieve": ["view_role"],
        "create": ["manage_role"],
        "update": ["manage_role"],
        "partial_update": ["manage_role"],
        "destroy": ["manage_role"],
    }

    queryset = Role.objects.exclude(role="admin")
    serializer_class = RoleSerializer
    pagination_class = PageNumberPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RoleDetailSerializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RoleSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            instance.refresh_from_db()
            RoleService.update_users(instance)

            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.role == "admin":
            return Response({"error": "Cannot delete the admin role."}, status=400)
        instance.delete()
        return Response({"message": "Role deleted successfully."}, status=204)

    def create(self, request, *args, **kwargs):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role = serializer.save()
            RoleService.update_users(role)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
