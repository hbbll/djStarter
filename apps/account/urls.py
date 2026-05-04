from django.urls import path
from .api.views.auth_views import login, register, AuthTokenObtainPairView, RefreshTokenUser, LogoutView, download_avatar
from .api.views.profile_views import profile, edit_profile
from .api.views.user_views import UserViewSet

urlpatterns = [
    # Authentication endpoints
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('token/', AuthTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', RefreshTokenUser.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Profile endpoints
    path('me/', profile, name='profile'),
    path('me/update/', edit_profile, name='edit_profile'),
    
    # Avatar endpoints
    path('avatar/<path:file_path>/', download_avatar, name='download_avatar'),
    
    # User management endpoints
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user_list'),
    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user_detail'),
]

