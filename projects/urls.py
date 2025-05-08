from django.urls import path
from .views import ClientView , ProjectView # Make sure views.py exists and has your view functions

urlpatterns = [
    path('clients/', ClientView.as_view(), name='client-list'),
    path('projects/', ProjectView.as_view(), name='project-list')
    # Add more paths as needed
]