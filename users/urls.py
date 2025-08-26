from django.urls import include, path
from .views import UserView, CustomTokenObtainPairView, UserProfileView



urlpatterns = [
    path('users/', UserView.as_view(), name='user-list'),
    # path('users/<int:pk>/', UserView.as_view(), name='user-detail'),
    # path('register/', UserView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]