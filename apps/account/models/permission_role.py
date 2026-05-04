from django.db import models
from .role import Role

class PermissionRole(models.Model):
    permission = models.CharField(max_length=50)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="permission_roles"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["permission", "role"], name="unique_permission_role"
            )
        ]
