from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken


def update_user_cache_data(user):
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    user_data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_superuser": user.is_superuser,
        "locale": user.locale,
        "is_staff": user.is_staff,
        "permissions": list(user.get_all_permissions()),
    }

    cache.set(token, user_data, timeout=60 * 60 * 24)
