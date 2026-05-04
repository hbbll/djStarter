from copy import copy

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.account.models import (
    Permission,
    PermissionRole,
    Role,
    PermissionGroup,
    CustomUser,
    UserRole,
)
from .seed_data import *


class Command(BaseCommand):
    help = "Seed database for testing and development."

    def handle(self, *args, **options):
        for group in permission_groups:
            code = group.get("code")
            translations = group.get("translations")
            group_obj, _ = PermissionGroup.objects.update_or_create(code=code)
            for lang_code, name in translations.items():
                group_obj.set_current_language(lang_code)
                group_obj.name = name
                group_obj.save()

            for permission in group.get("permissions"):
                Permission.objects.update_or_create(
                    permission=permission.get("permission"),
                    defaults={"name": permission.get("name"), "group": group_obj},
                )

        self.stdout.write(
            self.style.SUCCESS("PermissionGroup and Permission seeding completed.")
        )

        with transaction.atomic():
            for item in roles:
                role_data = copy(item)
                permissions = role_data.pop("permissions")
                name = role_data.pop("name")

                role_obj, created = Role.objects.get_or_create(
                    role=role_data["role"],
                )
                role_obj.set_current_language("en")
                role_obj.name = name
                role_obj.save()

                for perm in permissions:
                    if not PermissionRole.objects.filter(
                        role=role_obj, permission=perm
                    ).exists():
                        PermissionRole.objects.create(role=role_obj, permission=perm)

        self.stdout.write(self.style.SUCCESS("Role seeding completed."))

        for user_data in users:
            if not CustomUser.objects.filter(email=user_data["email"]).exists():
                user_role = Role.objects.get(role=user_data["role"])
                if user_data.get("is_superuser"):
                    CustomUser.objects.create_superuser(
                        email=user_data["email"],
                        password=user_data["password"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        locale=user_data["locale"],
                        role=user_role,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"Superuser '{user_data['email']}' created.")
                    )
                else:
                    CustomUser.objects.create_user(
                        email=user_data["email"],
                        password=user_data["password"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        locale=user_data["locale"],
                        role=user_role,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Regular user '{user_data['email']}' created."
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f"User '{user_data['email']}' already exists.")
                )

        for user_role in user_roles:
            try:
                user = CustomUser.objects.get(email=user_role["email"])
            except CustomUser.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"User '{user_role['email']}' not found for user_roles."
                    )
                )
                continue

            for role_code in user_role["roles"]:
                try:
                    role = Role.objects.get(role=role_code)
                except Role.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"Role '{role_code}' not found.")
                    )
                    continue

                _, created = UserRole.objects.get_or_create(user=user, role=role)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"UserRole: {user.email} → {role.role} created."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"UserRole: {user.email} → {role.role} already exists."
                        )
                    )
