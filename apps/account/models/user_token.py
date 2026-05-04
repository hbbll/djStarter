from django.db import models
from .custom_user import CustomUser

class UserToken(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tokens"
    )
    token = models.CharField(max_length=255)
    refresh = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
