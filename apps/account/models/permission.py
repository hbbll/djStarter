from django.db import models
from .permission_group import PermissionGroup


class Permission(models.Model):
    name = models.CharField(max_length=50)
    group = models.ForeignKey(
        PermissionGroup,
        on_delete=models.CASCADE,
        related_name="permissions",
        null=True,
        blank=True,
    )
    permission = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.name
