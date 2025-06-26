from .base import *
import os
# Debug mode ON for development
DEBUG = True
# Production settings
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_PYTHON_PROFILER_RESULT_PATH = os.path.join(MEDIA_ROOT, 'silk-profiles')
os.makedirs(SILKY_PYTHON_PROFILER_RESULT_PATH, exist_ok=True)
# Allow all hosts
ALLOWED_HOSTS = ["*"]

# SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  
    }
}

# database connection


# Email settings (use console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")


# CORS for local development
CORS_ORIGIN_ALLOW_ALL = True

# Cookie security OFF for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
    "rest_framework.authentication.SessionAuthentication")


print("Using development settings")
