from pathlib import Path
import os
import environ

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), ".env"))
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-ql486&8ag4a&c__u@awa-6q31mj0zpw1=!+usjvnk!l2=3+k7!'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #API DOCs
    'drf_spectacular',
    'drf_spectacular_sidecar',
    # Third-party
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'channels',
    'django_celery_results',
    # Local apps (order matters for template overrides)
    'core',
    'users',
    'projects', 
    'tasks',
    'services',
    'notifications',
    'reports',
    'adrf',
    'api'
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI_APPLICATION = 'tracker.wsgi.application'
# Replace WSGI with ASGI as default
# ASGI_APPLICATION = 'core.asgi.application'
ASGI_APPLICATION = "tracker.asgi.application"  # Point to your ASGI config
if "DATABASE_URL" in env:
    DATABASES = {"default": env.db()}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DJANGO_DATABASE_NAME", default="tracker"),
            "USER": env("DJANGO_DATABASE_USER", default="postgres"),
            "PASSWORD": env("DJANGO_DATABASE_PASSWORD", default="root"),
            "HOST": env("DJANGO_DATABASE_HOST", default="localhost"),
            "PORT": env("DJANGO_DATABASE_PORT", default="5432"),
        }
    }
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# channels layer 
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],  # Redis server address
            "symmetric_encryption_keys": [os.environ.get('CHANNELS_SECRET_KEY', 'default-secret-key')],
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Project Tracker API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # JWT Authentication Setup (used for docs, not actual auth)
    'AUTHENTICATION_WHITELIST': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    # Security Scheme for Swagger UI
    'COMPONENT_SPLIT_REQUEST': True,  # optional, helps with request/response schemas
    'SECURITY_SCHEMES': {
        'JWT': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',  # Optional, but improves clarity in Swagger UI
        }
    },

    # Apply the JWT security scheme globally to all endpoints
    'SECURITY': [{'JWT': []}],

    # Swagger UI settings
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}
