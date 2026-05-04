from rest_framework import serializers
from apps.account.models import CustomUser, Role, Permission, PermissionGroup
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "is_active",
            "locale",
            "is_staff",
            "is_superuser",
            "password",
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"
        read_only_fields = ("id",)


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "is_active",
            "locale",
            "is_staff",
            "is_superuser",
            "password",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class RoleSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Role
        fields = [
            "role",
            "name",
            "priority",
        ]


class RoleDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="name")

    class Meta:
        model = Role
        fields = [
            "role",
            "name",
            "priority",
        ]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["name", "permission", "group"]


class PermissionGroupSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=PermissionGroup)
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PermissionGroup
        fields = ["code", "translations", "permissions"]

    def get_permissions(self, obj):
        return PermissionSerializer(obj.permissions.all(), many=True).data
