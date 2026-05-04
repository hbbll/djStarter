from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from config.permissions import HasUserPermission
from apps.account.api.serializers import *
from apps.account.models import *
from apps.account.api.service import UserService


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def edit_profile(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        try:
            with transaction.atomic():
                serializer.save()
            return Response(
                {
                    "status": 1,
                    "msg": "User profile updated successfully",
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": 0, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(
        {"status": 0, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    user_data = UserSerializer(user).data

    return Response(
        {
            "status": 1,
            "msg": "Profile data",
            "user": user_data,
        },
        status=status.HTTP_200_OK,
    )


class MeView(APIView):
    permission_classes = [HasUserPermission]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        token = request.auth
        response = UserService.get_user_by_token(token)

        # grpc_client = GRPCClient()
        # params = {'method': "users", 'filter':{'id':1}}
        # user_data['grpc'] = grpc_client.get_data(params=params)
        if response.get("success"):
            return Response(response, status=200)
        return Response(response, status=404)

    def patch(self, request):
        token = request.auth
        response = UserService.get_user_by_token(token)

        if response.get("success"):
            user_id = response.get("data").get("id")
            user = CustomUser.objects.get(id=user_id)
            editable_fields = [
                "image",
                "old_password",
                "new_password",
                "new_password_confirm",
            ]
            data = request.data.copy()
            for field in list(data.keys()):
                if field not in editable_fields:
                    data.pop(field)
            serializer = UserCreateUpdateSerializer(
                user, data=data, context={"request": request}, partial=True
            )
            serializer.is_valid(raise_exception=True)
            response = UserService.save_user(serializer.validated_data, user)
            if response.get("success"):
                return Response(response, status=200)
        return Response(response, status=400)
