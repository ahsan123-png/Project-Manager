from django.urls import path
from . import views  # Make sure views.py exists and has your view functions

urlpatterns = [
    path('', views.home, name='project_list'),
    # Add more paths as needed
]