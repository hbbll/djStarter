from django.contrib import admin
from apps.account.models import (
    CustomUser,
    Role,
    PermissionUser,
    PermissionGroup,
    Permission,
    UserRole,
    PermissionRole,
    UserToken,
)
from parler.admin import TranslatableAdmin
from django.contrib.auth.models import Group

admin.site.unregister(Group)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "created_at",
    )
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "created_at")
    ordering = ("-created_at",)


@admin.register(Role)
class RoleAdmin(TranslatableAdmin):
    list_display = ("role", "get_name", "priority")

    def get_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True)

    get_name.short_description = "Name"


class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 1
    fields = ("permission", "name")


@admin.register(PermissionGroup)
class PermissionGroupAdmin(TranslatableAdmin):

    search_fields = ("code",)

    def list_permissions(self, obj):
        return ", ".join([p.permission for p in obj.permissions.all()])

    list_permissions.short_description = "Permissions"
    list_display = ("code", "list_permissions")
    inlines = [PermissionInline]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("permission", "name", "group")
    search_fields = ("permission", "name")
    list_filter = ("group",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__email", "role__role")


@admin.register(PermissionRole)
class PermissionRoleAdmin(admin.ModelAdmin):
    list_display = ("permission", "role")
    search_fields = ("permission", "role__role")


@admin.register(PermissionUser)
class PermissionUserAdmin(admin.ModelAdmin):
    list_display = ("permission", "user")
    search_fields = ("permission", "user__email")


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at")
    search_fields = ("user__email", "token")
    ordering = ("-created_at",)
