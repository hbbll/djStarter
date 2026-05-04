from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .role import Role
from ..managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255, null=True)
    avatar = models.URLField(max_length=2024,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    locale = models.CharField(max_length=20, default="ru")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email
