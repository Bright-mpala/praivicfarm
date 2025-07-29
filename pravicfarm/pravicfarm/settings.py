
import os
from pathlib import Path

# BASE DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = 'your-secret-key'  # Replace with your actual secret key
DEBUG = True
ALLOWED_HOSTS = []

# APPLICATIONS
INSTALLED_APPS = [
    'jazzmin',  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', 
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'ckeditor',
    'core',
    'channels',  # For WebSocket support
]
SITE_ID = 1  

ASGI_APPLICATION = 'pravicfarm.asgi.application'
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
} 
# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # <-- Make sure you want this middleware
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLS
ROOT_URLCONF = 'pravicfarm.urls'

    # settings.py
TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')], 
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'django.template.context_processors.request',

                ],
            },
        },
    ]

# WSGI
WSGI_APPLICATION = 'pravicfarm.wsgi.application'

# DATABASE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# AUTHENTICATION
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',  # needed for allauth
)

# LOGIN / LOGOUT REDIRECT
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'account_login'  # Use allauth's login URL
LOGOUT_URL = 'account_logout'  # Use allauth's logout URL

# AUTH USER SETTINGS
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_REDIRECT_URL = '/'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  

# EMAIL SETTINGS (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'infopraivicfarm@gmail.com'
EMAIL_HOST_PASSWORD = 'taxwhticeijcbdsx'  # Use your generated Gmail app password here
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_NOTIFY_EMAIL = 'infopraivicfarm@gmail.com' # Email to notify on contact form submissions
# STATIC / MEDIA
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# LANGUAGE / TIMEZONE
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Harare'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# DEFAULT AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# MESSAGE TAGS for Bootstrap
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}
#Django ckeditor settings
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join([
            'codesnippet',
        ]),
        'codeSnippet_theme': 'monokai_sublime',
        'removePlugins': 'elementspath',
        'allowedContent': True,
        'autoParagraph': False,
        'forcePasteAsPlainText': True,
        
    },
}
# JAZZMIN ADMIN SETTINGS (optional)
JAZZMIN_SETTINGS = {
    "site_title": "Pravic Poultry Admin",
    "site_header": "Pravic Poultry Dashboard",
    "site_brand": "Pravic Farm",
    "site_logo": "images/logo.jpg",     # Ensure this path is correct
    "welcome_sign": "Welcome to Pravic Poultry Farm Admin",
    "copyright": "Pravic Farm © 2025",
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "core.Product": "fas fa-box",
        "core.BlogPost": "fas fa-newspaper",
        "core.ContactMessage": "fas fa-envelope",
        "core.Subscriber": "fas fa-envelope-open-text",
        "core.Order": "fas fa-shopping-cart",
        "core.GalleryImage": "fas fa-image",
        "core.Review": "fas fa-star",
        "core": "fas fa-home",
        "sites": "fas fa-globe",
        "flatpages": "fas fa-file-alt",
        "admin": "fas fa-cogs",
        "jazzmin": "fas fa-tachometer-alt",
        "jazzmin.settings": "fas fa-cog",
        "jazzmin.theme": "fas fa-palette",
        "jazzmin.customization": "fas fa-sliders-h",
        "jazzmin.navigation": "fas fa-bars",
        "jazzmin.topmenu": "fas fa-th-list",
        "jazzmin.sidebar": "fas fa-columns",
        "jazzmin.footer": "fas fa-info-circle",
        "jazzmin.dashboard": "fas fa-tachometer-alt",
        "jazzmin.notifications": "fas fa-bell",
        "jazzmin.users": "fas fa-users",
        "jazzmin.groups": "fas fa-users-cog",
        "jazzmin.permissions": "fas fa-lock",
        "jazzmin.logs": "fas fa-file-alt",
    },
    "topmenu_links": [
        {"name": "Home", "url": "/", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app": "blog"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "order_with_respect_to": ["auth", "blog", "products", "orders"],
    "theme": "litera",  
    "theme_options": {
        "navbar_fixed": True,
        "sidebar_fixed": True,
        "footer_fixed": False,
    },
}

CKEDITOR_UPLOAD_PATH = "uploads/"
