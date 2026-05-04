from django.core.cache import cache

from apps.account.models import UserToken, CustomUser
from apps.account.api.serializers import UserDetailSerializer
from config import settings


class UserCacheManager:
    @staticmethod
    def get_user_data(token):
        user_data = cache.get(str(token))
        return user_data

    @staticmethod
    def create_user_cache(user):
        tokens = UserToken.objects.filter(user=user)
        user_data = UserDetailSerializer(user).data
        for token in tokens:
            cache.set(str(token.token), user_data, timeout=settings.CACHE_TIMEOUT)

    @staticmethod
    def cache_user_token(user_id, token):
        user = CustomUser.objects.get(id=user_id)
        user_data = UserDetailSerializer(user).data
        cache.set(token, user_data, timeout=settings.CACHE_TIMEOUT)


    @staticmethod
    def clear_user_cache(token):
        user_data = cache.get(str(token))
        if user_data:
            cache.delete(str(token))

    @staticmethod
    def invalidate_user_cache(user):
        user_tokens = UserToken.objects.filter(user=user)
        for user_token in user_tokens:
            cache.delete(str(user_token.token))
