from django.core.management.base import BaseCommand
from apps.account.models import (
    Permission,
    PermissionRole,
    Role,
    PermissionGroup,
    CustomUser,
    UserRole,
)
from .seed_data import permission_groups, roles, users


class Command(BaseCommand):
    help = "Unseed database (remove seeded test data)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting unseeding process..."))

        # Delete UserRoles if model exists
        if UserRole in CustomUser._meta.related_objects:
            for user in users:
                try:
                    obj = CustomUser.objects.get(email=user["email"])
                    UserRole.objects.filter(user=obj).delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"Deleted UserRoles for: {user['email']}")
                    )
                except CustomUser.DoesNotExist:
                    pass

        # Delete users
        for user in users:
            try:
                obj = CustomUser.objects.get(email=user["email"])
                obj.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted user: {user['email']}"))
            except CustomUser.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"User not found: {user['email']}")
                )

        # Delete permission-role mappings
        deleted_roles = PermissionRole.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted_roles[0]} PermissionRole mappings.")
        )

        # Delete roles
        for role in roles:
            try:
                obj = Role.objects.get(role=role["role"])
                obj.delete()
                self.stdout.write(self.style.SUCCESS(f"Deleted role: {role['role']}"))
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Role not found: {role['role']}"))

        # Delete permissions and groups
        for group in permission_groups:
            try:
                group_obj = PermissionGroup.objects.get(code=group["code"])
                permissions = Permission.objects.filter(group=group_obj)
                count = permissions.count()
                permissions.delete()
                group_obj.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Deleted group: {group['code']} and {count} related permissions."
                    )
                )
            except PermissionGroup.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Group not found: {group['code']}")
                )

        self.stdout.write(self.style.SUCCESS("✅ Unseeding completed successfully."))
