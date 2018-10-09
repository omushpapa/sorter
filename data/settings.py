import os
from pyconfigreader import ConfigReader

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings_ini = os.path.join(PROJECT_ROOT, 'config.ini')

with ConfigReader(settings_ini) as config:
    log_file = config.get('log_file', default='sorter.logs', default_commit=True)
    DEBUG = config.get('debug', default='False')

    SETTINGS = {
        'cleanup': config.get('cleanup', default='True'),
        'autoscroll': config.get('autoscroll', default='True', section='progress'),
        'scrollbar': config.get('scrollbar', default='False', section='progress'),
    }

if os.name == 'nt':
    app_data = os.getenv('APPDATA')
    PROJECT_ROOT = os.path.join(app_data, 'Sorter')
    try:
        os.mkdir(PROJECT_ROOT)
    except FileExistsError:
        pass

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

LOG_FILE = os.path.join(PROJECT_ROOT, log_file)

SORTER_IGNORE_FILENAME = '.signore'		# Should start with a dot

SORTER_FOLDER_IDENTITY_FILENAME = '.sorter'		# Should start with a dot

MIDDLEWARE_CLASSES = []
