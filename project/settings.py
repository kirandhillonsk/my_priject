

import os
import pymysql
import environ
env = environ.Env()
environ.Env.read_env()

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

pymysql.install_as_MySQLdb()
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


SITE_ID = 1
# Application definition

INSTALLED_APPS = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_crontab',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'rest_framework',
    'django.contrib.humanize',
    'accounts',
    'enduser',
    'rvt_lvt',
    'faq',
    'rating',
    'blog',
    'page',
    'superuser',
    'frontend',
    'api',
    'backup',
    'history',
    'chat',
    'contact',
    'notification',
    'gcalender',
    'impersonate'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware'
]

ROOT_URLCONF = 'project.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

AUTH_USER_MODEL = "accounts.User"
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xxx',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'CONN_MAX_AGE': 600,
        'OPTIONS':{"init_command":"SET foreign_key_checks = 0;",'charset': 'utf8mb4'}
    }
}

AUTHENTICATION_BACKENDS = [
    'accounts.backend.EmailLoginBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

SOCIALACCOUNT_LOGIN_ON_GET=True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATIC_URL = '/static/'

if not DEBUG:
    STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static", "admin"),
    )

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
else:
     
    STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static", "admin"),
    os.path.join(BASE_DIR, 'static'),
    )


MEDIA_URL = '/media/'
MEDIA_ROOT = (
    os.path.join(BASE_DIR, 'media')
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
       'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

USE_X_FORWARDED_HOST = True

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'mail.privateemail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'admin@.org'
# EMAIL_HOST_PASSWORD = 'admin@123'
# EMAIL_USE_TLS = True

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True  
# EMAIL_HOST = 'j6.jiweb.in'  
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'test2@toxsl.in'
# EMAIL_HOST_PASSWORD = 'iYuoXv0t'

CRONJOBS = [
    ('* 9 * * *', 'enduser.crons.early_notiifcation'),
]

