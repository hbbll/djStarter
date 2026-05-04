from django.db import models
from .custom_user import CustomUser
from .role import Role


class UserRole(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="user_roles"
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "role"], name="unique_user_role")
        ]
