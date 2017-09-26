import os

USER = 'root'
HOST = '104.236.41.188'

CURRENT_HOST = 'steepshot.io'

# KEY_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'private.key')
KEY_FILENAME = '~/.ssh/id_rsa'

REPOSITORY = 'https://github.com/Chainers/steepshot.io'

PROJECT_NAME = 'steepshot_io'


# We use non-root user for better security
DEPLOYMENT_USER = 'steepshot_io'
DEPLOYMENT_GROUP = 'steepshot_io'

REMOTE_DEPLOY_DIR = os.path.join('/home', DEPLOYMENT_USER)

USER_PROFILE_FILE = os.path.join(REMOTE_DEPLOY_DIR, '.profile')

DEPLOY_DIR = os.path.join(REMOTE_DEPLOY_DIR, PROJECT_NAME)

MEDIA_ROOT = os.path.join(DEPLOY_DIR, 'uploads')
MEDIA_URL = '/uploads/'

STATIC_ROOT = os.path.join(DEPLOY_DIR, 'staticfiles')
STATIC_URL = '/static/'

UBUNTU_PACKAGES = [
    'git',
    'python-pip',
    'python3-dev',
    'libpq-dev',
    'nginx',
    'postgresql-9.5',
    'python3.5',
    'libmemcached-dev',
    'zlib1g-dev',
    'upstart',
    'redis-server',
    'systemd-sysv',
    # 'upstart-sysv'
    'python-certbot-nginx',
]

WORKON_HOME = os.path.join(REMOTE_DEPLOY_DIR, '.virtualenvs')
ENV_NAME = PROJECT_NAME
VENV_BIN_DIR = os.path.join(WORKON_HOME, ENV_NAME, 'bin')
VENV_ACTIVATE = os.path.join(VENV_BIN_DIR, 'activate')

ENV_PATH = os.path.join(WORKON_HOME, ENV_NAME)

LOCAL_CONF_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf_templates')


DB_HOST = 'localhost'
DB_USER = 'steepshot_io'
DB_PASSWORD = 'ZmNiOTllMDZhYzg1OGFjYzU4ZDc4ZWNi'
DB_NAME = 'steepshot_io'

DATABASE_URL = 'postgres://%s:%s@%s/%s' % (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

# Systemd service name
BACKEND_SERVICE = 'steepshot_io.service'

# Systemd service name
CELERY_SERVICE = 'celery.service'

GUNI_PORT = 8001
GUNI_WORKERS = 3
GUNI_TIMEOUT = 60
GUNI_GRACEFUL_TIMEOUT = 180

SETTINGS_MODULE = 'steepshot_io.prod_settings'
GOLOS_SETTINGS_MODULE = 'steepshot_io.golos_prod_settings'


ENVIRONMENTS = {
    'PROD': {
        'HOST': HOST,
        'SSH_PORT': '22',
        'USER': USER,
        'GIT_BRANCH': 'master',
        'CURRENT_HOST': 'steepshot.io',
        'SETTINGS_MODULE': SETTINGS_MODULE,
        'KEY_FILENAME': KEY_FILENAME,
        'IS_CERTBOT_CERT': True,
    },
    'SPA': {
        'HOST': HOST,
        'SSH_PORT': '22',
        'USER': USER,
        'CURRENT_HOST': 'alpha.steepshot.io',
        'SETTINGS_MODULE': SETTINGS_MODULE,
        'GIT_BRANCH': 'master',
        'KEY_FILENAME': KEY_FILENAME,
    }
}

WEBAPP_HOST = 'alpha.steepshot.io'
WEBAPP_STATIC_DIR = '/home/steepshot_io/frontend'
