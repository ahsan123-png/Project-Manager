from django.urls import path
from .views import ServiceCRUDView

urlpatterns = [
    path('services/', ServiceCRUDView.as_view(), name='service-crud'),
]
