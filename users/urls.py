from django.urls import path
from .views import UserView, CustomTokenObtainPairView, UserProfileView

urlpatterns = [
    path('register/', UserView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]