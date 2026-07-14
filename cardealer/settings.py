from pathlib import Path
import os
import secrets
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
# Must be supplied via the SECRET_KEY environment variable in production.
# Only DEBUG runs get a randomly generated fallback (new on every process
# start, never written to disk) so local development works without an
# .env file - nothing secret is ever hardcoded in source.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError(
            'SECRET_KEY environment variable is required when DEBUG=False.'
        )
    SECRET_KEY = secrets.token_urlsafe(50)

ALLOWED_HOSTS = [h for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h]
# Vercel deployments (production + every preview URL)
ALLOWED_HOSTS += ['.vercel.app']
# Deploying on render cloud host
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if DEBUG:
    ALLOWED_HOSTS.append('*')

CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o
]
CSRF_TRUSTED_ORIGINS += ['https://*.vercel.app']

# Vercel terminates TLS in front of the app and forwards over HTTP, so trust
# its X-Forwarded-Proto header to know a request was actually made over HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    # 'django_crontab', #for scheduled job specially for backup database
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # must come before staticfiles per django-cloudinary-storage docs
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'car.apps.CarConfig',
    'django.contrib.humanize', # used in templates, html files-> adds coma to numbers
    # 'import_export', # import export csv file button in django admin section
    # 'dbbackup',  # django-dbbackup
]

# django-dbbackup
# https://django-dbbackup.readthedocs.io/en/master/installation.html
# DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
# DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR/'backup'}

# django crontab job scheduling
# does NOT work on windows
# CRONJOBS = [
#     ('*/1 * * * *', 'cardealer.cron.my_scheduled_job')
# ]   # some crontab terminal commands 
# https://pypi.org/project/django-crontab/
# python manage.py crontab add
# python manage.py crontab show
# python manage.py crontab remove


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cardealer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # added templates path
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'car.context_processors.ad_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'cardealer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if os.environ.get('DATABASE_URL'):
    # Vercel's filesystem is read-only/ephemeral, so production always needs
    # an external database reachable via DATABASE_URL (e.g. Neon, Supabase).
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

# `manage.py collectstatic` writes here at build time. Vercel's static build
# step (see build_files.sh / vercel.json) publishes this directory directly
# from its CDN, so the app server itself never needs to serve static files.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Media files (user-uploaded car photos)
# Vercel's filesystem is read-only/ephemeral outside of /tmp, so uploads
# can't be stored locally in production - they're pushed to Cloudinary
# instead whenever CLOUDINARY_URL is configured. Falls back to local disk
# storage for local development.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

if os.environ.get('CLOUDINARY_URL'):
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


#temp
# RuntimeError at /submit_number/3
# You called this URL via POST, but the URL doesn't end in a slash and you have APPEND_SLASH set. 
# Django can't redirect to the slash URL while maintaining POST data. 
# Change your form to point to 127.0.0.1:8000/submit_number/3/ (note the trailing slash),
#  or set APPEND_SLASH=False in your Django settings.    
APPEND_SLASH=False

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# HTTPS settings for production
# Vercel always serves over HTTPS, so lock these down whenever DEBUG is off.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# SESSION_COOKIE_SECURE: ensures a secure session cookie is used
# CSRF_COOKIE_SECURE: ensures a secure CSRF cookie is used
# SECURE_SSL_REDIRECT: all non-HTTP requests are redirect to HTTPS


# HSTS settings
# SECURE_HSTS_SECONDS = 31536000 # 1 year
# SECURE_HSTS_PRELOAD = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# SECURE_HSTS_SECONDS: prevents browsers from connecting to your website with an insecure connection for the specified duration in seconds
# SECURE_HSTS_PRELOAD: the preload directive is added to the HSTS header
# SECURE_HSTS_INCLUDE_SUBDOMAINS: the includeSubDomains directive is added to the HSTS header
