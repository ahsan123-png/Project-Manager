
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),  # Your API endpoints
    path('project/', include('projects.urls')),  # Your API endpoints
    path('api/auth/', include('users.urls')),  # Your API endpoints
    # path('api/docs/', include('api.schema_urls')),  # Docs
]
