from django.db import models
from .custom_user import CustomUser

class PermissionUser(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="permission_users"
    )
    permission = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "permission"], name="unique_permission_user")
        ]
