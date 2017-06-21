import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'operations.db'),
    }
}

INSTALLED_APPS = (
    'data',
)

SECRET_KEY = '63cFWu$$lhT3bVP9U1k1Iv@Jo02SuM'

LOG_FILE = os.path.join(PROJECT_ROOT, 'sorter.logs')

SORTER_IGNORE_FILENAME = '.signore'
