import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker.settings')  # Make sure this matches your settings module

application = get_asgi_application()