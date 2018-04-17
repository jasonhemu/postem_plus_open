# Using a placeholder for environment variables.
# If not found in the environment, it will default to the local value, which is set in
# the second parameter. Example:
# os.environ.get("ENVIRONMENT_KEY", "LOCAL_VALUE")
# This makes it a bit easier to use one file for local and environment deployment.

# Declare your consumer key and shared secret. If you end
# up having multiple consumers, you may want to add separate
# key/secret sets for them.

# Configuration for LTI
CONSUMER_KEY = ''
SHARED_SECRET = ''

# Configuration for PYLTI

PYLTI_CONFIG = {
    'consumers': {
        CONSUMER_KEY: {
            'secret': SHARED_SECRET
        }
        # Feel free to add more key/secret pairs for other consumers.
    }
}


# Secret key used for Flask sessions, etc. Must stay named 'secret_key'.
# Can be any randomized string, recommend generating one with os.urandom(24)
secret_key = ''

# Application Logging
LOG_FILE = 'error.log'
LOG_FORMAT = '%(asctime)s [%(levelname)s] {%(filename)s:%(lineno)d} %(message)s'
LOG_LEVEL = 'INFO'
LOG_MAX_BYTES = 1024 * 1024 * 5  # 5 MB
LOG_BACKUP_COUNT = 1

# Configuration for Canvas API
CANVAS_API_URL = ''
CANVAS_API_KEY = ''
HEADERS = {'Authorization':'Bearer ' + CANVAS_API_KEY}

# Configuration for File Upload with AWS S3
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY =''
BUCKET = ''
ALLOWED_EXTENSIONS = set(['csv'])
