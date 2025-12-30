from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-+dwss0bbja9c-1xyz(n0@r(e6o(4e*z2=t$xm6w*nr9+ygm$4p"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# --- Caching Settings ---
# (This is DIFFERENT from production)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'elevate-development-cache',
    }
}



# --- Local Settings Import ---
try:
    from .local import *
except ImportError:
    pass
