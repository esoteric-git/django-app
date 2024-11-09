from ocean_analytics.settings import *

# Use an in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

# Disable debugging for tests
DEBUG = False

# Use a constant secret key for tests
SECRET_KEY = 'test-key-not-for-production'

# Required for running tests
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' 