from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from django.core.cache import cache
from django.utils import translation
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from config import settings
from apps.account.api.serializers import *
from apps.account.models import *
from apps.account.utils import UserCacheManager
from config.log_change import log_change
from django.http import JsonResponse, HttpResponse
from minio.error import S3Error
import mimetypes
import os
from apps.account.api.service import upload_user_avatar, get_minio_client


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


@api_view(["POST"])
@permission_classes(
    [
        AllowAny,
    ]
)
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"status": 0, "error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not is_valid_email(email):
        return Response(
            {"status": 0, "error": "The email format is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(email=email, password=password)

    if user:
        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            UserToken.objects.create(
                user=user, token=access_token, refresh=refresh_token
            )
            UserCacheManager.cache_user_token(user.id, access_token)
            return Response(
                {
                    "status": 1,
                    "msg": "User signed in",
                    "user": UserSerializer(user).data,
                    "refresh": refresh_token,
                    "access": access_token,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": 0, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return Response(
            {"status": 0, "msg": "Incorrect email or password"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    email = request.data.get("email")
    locale = request.data.get("locale")

    password = request.data.get("password")

    if not first_name or not password or not email:
        return Response(
            {"status": 0, "msg": "First name, password and email required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    avatar = request.FILES.get("avatar")
    if not avatar:
        return Response(
            {"status": 0, "msg": "Avatar upload required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if CustomUser.objects.filter(first_name=first_name).exists():
        return Response(
            {"status": 0, "msg": "First name already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if CustomUser.objects.filter(email=email).exists():
        return Response(
            {"status": 0, "msg": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return Response(
            {"status": 0, "msg": "Password must be at least 8 characters long"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"status": 0, "msg": "Invalid email address"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    try:
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                locale=locale,
                password=password,
            )

            # Profile.objects.create(user=user, ...)
            upload_result = upload_user_avatar(user.id, avatar)
            if not upload_result["success"]:
                return JsonResponse({"error": upload_result["error"]}, status=500)

            user.avatar = upload_result["url"]
            user.save(update_fields=["avatar"])

            refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": 1,
                "msg": "User registered and Avatar upload successfully",
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "avatar_url": upload_result["url"]
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"status": 0, "msg": "Registration failed", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_avatar(request, file_path):
    client = get_minio_client()
    if "/" not in file_path:
        return JsonResponse(
            {"error": "Path noto'g'ri formatda. Masalan: bucket/folder/file.jpg"},
            status=400
        )
    bucket_name, object_path = file_path.split("/", 1)
    try:
        data = client.get_object(bucket_name, object_path)
        mime_type, _ = mimetypes.guess_type(object_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        response = HttpResponse(data.read(), content_type=mime_type)
        response["Content-Disposition"] = f'inline; filename="{os.path.basename(object_path)}"'
        data.close()
        data.release_conn()
        return response
    except S3Error:
        return JsonResponse({"error": "Fayl topilmadi"}, status=404)


class AuthTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data
        access_token = data["access"]

        new_locale = request.data.get("locale")
        if new_locale in dict(settings.LANGUAGES):
            serializer.user.locale = new_locale
            serializer.user.save()
            serializer.user.refresh_from_db()
            translation.activate(new_locale)

        user_tokens = UserToken.objects.filter(user=serializer.user)
        for user_token in user_tokens:
            if cache.get(str(user_token.token)) is None:
                user_token.delete()

        UserToken.objects.create(
            user=serializer.user, token=access_token, refresh=data["refresh"]
        )

        UserCacheManager.create_user_cache(serializer.user)

        ip_address = request.META.get("REMOTE_ADDR")
        log_change(
            user=serializer.user,
            ip=ip_address,
            object_name="User",
            object_id=serializer.user.id,
            action_type="login",
            data={"message": "Foydalanuvchi tizimga kirdi"},
        )

        user_serializer = UserDetailSerializer(serializer.user)
        data["user"] = user_serializer.data
        return Response(data)


class RefreshTokenUser(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        user_token = UserToken.objects.filter(refresh=refresh_token).first()

        if not user_token:
            raise InvalidToken("Refresh token is invalid or not found.")

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data

        UserCacheManager.clear_user_cache(user_token.token)

        user_token.token = data["access"]
        user_token.save()

        UserCacheManager.create_user_cache(user_token.user)

        ip_address = request.META.get("REMOTE_ADDR")
        log_change(
            user=user_token.user,
            ip=ip_address,
            object_name="User",
            object_id=user_token.user_id,
            action_type="login",
            data={"message": "Foydalanuvchi refresh token qildi"},
        )

        return Response({"access": user_token.token})


class LogoutView(APIView):
    def post(self, request):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                return Response(
                    {"error": "Authentication credentials were not provided"},
                    status=400,
                )

            token = auth_header.split(" ")[1]
            user_token = UserToken.objects.get(token=token)

            user = user_token.user
            ip_address = request.META.get("REMOTE_ADDR")

            log_change(
                user=user,
                ip=ip_address,
                object_name="User",
                object_id=user.id,
                action_type="logout",
                data={"message": "Foydalanuvchi tizimdan chiqdi"},
            )

            UserCacheManager.clear_user_cache(token)
            user_token.delete()
            request.session.flush()
            return Response({"message": "Logged out successfully."}, status=200)
        except UserToken.DoesNotExist:
            return Response({"error": "Invalid token."}, status=400)
