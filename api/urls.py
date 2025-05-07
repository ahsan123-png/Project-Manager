from django.urls import path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Schema endpoint
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI
    path('docs/', SpectacularSwaggerView.as_view(
        url_name='schema',
        authentication_classes=[],  # Disable auth for docs page itself
    ), name='swagger-ui'),
    
    # Your other URLs...
]