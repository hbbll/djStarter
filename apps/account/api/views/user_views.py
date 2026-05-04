from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.utils import translation
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from apps.account.signals import update_user_cache_data
from config import settings
from apps.account.api.filters import UserFilter
from config.authentication import CustomBearerAuthentication
from config.permissions import HasUserPermission
from config.views import BasePermissionModelViewSet
from config.pagination import PageNumberPagination
from apps.account.api.serializers import *
from apps.account.models import *
from apps.account.utils import UserCacheManager
from config.log_change import log_change
from rest_framework import status as http_status
from apps.account.api.service import UserService
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from apps.account.api.service import upload_user_avatar


class UserViewSet(BasePermissionModelViewSet):
    required_permissions = {
        "list": ["view_user"],
        "retrieve": ["view_user"],
        "create": ["manage_user"],
        "update": ["manage_user"],
        "partial_update": ["manage_user"],
        "destroy": ["manage_user"],
    }
    parser_classes = (MultiPartParser, FormParser)
    queryset = CustomUser.objects.filter(is_superuser=False)
    pagination_class = PageNumberPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = UserFilter
    search_fields = ["first_name", "last_name", "email"]
    ordering = ("-created_at",)

    def get_object(self):
        queryset = CustomUser.objects.all()
        obj = get_object_or_404(queryset, pk=self.kwargs.get("pk"))
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UserCreateUpdateSerializer
        return UserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def list(self, request, *args, **kwargs):
        auth_user = request.user
        queryset = self.filter_queryset(self.get_queryset())

        if not (auth_user.is_superuser or auth_user.is_staff):
            department_id = auth_user.get("department", {}).get("id")
            if department_id:
                queryset = queryset.filter(department=department_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserDetailSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = UserService.save_user(serializer.validated_data)

        if not response.get("success"):
            return Response(response, status=400)

        return Response(response, status=200)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserCreateUpdateSerializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        user_id = instance.id
        validated_data = serializer.validated_data
        avatar = request.FILES.get("avatar")
        if avatar:
            upload_result = upload_user_avatar(user_id, avatar)

            if not upload_result["success"]:
                return JsonResponse({"error": upload_result["error"]}, status=500)
            validated_data["avatar"] = upload_result["url"]

        response = UserService.save_user(validated_data, instance)

        if not response.get("success"):
            return Response(response, status=400)

        return Response(response, status=200)

    @action(detail=False, methods=["get"], url_path="subordinates")
    def subordinates(self, request):
        auth_user = request.user
        roles = auth_user.get("roles", [])

        role_objects = Role.objects.filter(role__in=roles)
        priority_values = list(role_objects.values_list("priority", flat=True))
        user_min_priority = min(priority_values) if priority_values else float("inf")

        users_query = CustomUser.objects.filter(is_active=True)

        users = users_query.values(
            "id",
            "first_name",
            "last_name",
        )
        return Response({"subordinates": users})

    @action(detail=False, methods=["get"], url_path="assignees(?:/(?P<pk>[^/.]+))?")
    def assignees(self, request, pk=None):
        if pk:
            users_query = CustomUser.objects.filter(
                is_active=True, department__id=pk
            ).distinct()
        else:
            users_query = CustomUser.objects.filter(is_active=True).distinct()

        users = users_query.values(
            "id",
            "first_name",
            "last_name",
        )
        return Response({"assignees": users})


class AdminLoginAsUser(APIView):
    authentication_classes = [CustomBearerAuthentication]

    def post(self, request, *args, **kwargs):
        auth_user = request.user
        if not auth_user.is_superuser:
            return Response(
                {"error": "You have no permission to perform this action"},
                status=http_status.HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"error": "User id is required"},
                status=http_status.HTTP_400_BAD_REQUEST,
            )

        user = CustomUser.objects.get(id=user_id)
        refresh_token = RefreshToken.for_user(user)
        access_token = str(refresh_token.access_token)

        UserToken.objects.create(user=user, token=access_token)
        UserCacheManager.create_user_cache(user)
        ip_address = request.META.get("REMOTE_ADDR")
        log_change(
            user=user,
            ip=ip_address,
            object_name="User",
            object_id=user.id,
            action_type="login",
            data={"message": "Admin tizimga foydalanuvchi nomidan kirdi"},
        )
        user_serializer = UserDetailSerializer(user)
        data = {
            "refresh": str(refresh_token),
            "access": access_token,
            "user": user_serializer.data,
        }
        return Response(data)


class SetLocaleView(APIView):
    permission_classes = [HasUserPermission]

    def post(self, request):
        user_data = request.user
        user = CustomUser.objects.get(id=user_data.get("id"))

        new_locale = request.data.get("locale", "ru")
        if new_locale not in dict(settings.LANGUAGES):
            return Response({"error": "Invalid locale"}, status=400)
        translation.activate(new_locale)

        user.locale = new_locale
        user.save()
        update_user_cache_data(user)

        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
