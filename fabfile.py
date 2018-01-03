import datetime
import logging
import os
import sys

from fabric.api import env, lcd, task, sudo, local, prefix, cd, settings, require
from fabric.contrib.files import upload_template, contains, append, exists
from fabric.operations import put, prompt

from steepshot_io.deploy_settings import (
    USER, WEB_HOST, LANDING_HOST, REMOTE_DEPLOY_DIR, PROJECT_NAME, REPOSITORY,
    DEPLOY_DIR, UBUNTU_PACKAGES, WORKON_HOME, ENV_NAME, LOCAL_CONF_DIR,
    ENV_PATH, DATABASE_URL, DB_USER, DB_PASSWORD, DB_NAME,
    GUNI_PORT, GUNI_WORKERS, GUNI_TIMEOUT, GUNI_GRACEFUL_TIMEOUT,
    STATIC_ROOT, STATIC_URL, MEDIA_ROOT, MEDIA_URL,
    DEPLOYMENT_USER, DEPLOYMENT_GROUP, ENVIRONMENTS,
    USER_PROFILE_FILE, VENV_ACTIVATE,
    BACKEND_SERVICE, CELERY_SERVICE,
    WEBAPP_STATIC_DIR,
)

# This allows us to have .profile to be read when calling sudo
# and virtualenvwrapper being activated using non-SSH user
SUDO_PREFIX = 'sudo -i'
FRONTEND_LOCAL_DIR = os.path.abspath(os.path.join('..', 'steepshot-web'))
FRONTEND_BUILD_COMMAND = 'gulp build'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fabfile')


def _get_current_datetime() -> str:
    now = datetime.datetime.now()
    return now.strftime('%d-%m-%Y_%H-%M-%S')


def _get_systemd_service_path(service_name):
    if not service_name.endswith(('.service', '.unit')):
        service_name += '.service'
    return '/etc/systemd/system/{}'.format(service_name)


def _load_environment(env_name: str):
    """
    Sets specified environment
    """
    if env_name not in ENVIRONMENTS:
        raise ValueError("Incorrect environment name ({}). "
                         "Valid options are: {}"
                         .format(env_name, ENVIRONMENTS.keys()))
    _env = ENVIRONMENTS[env_name]
    env.user = _env['USER']
    env.hosts = ["{host}:{port}".format(host=_env['HOST'],
                                        port=_env['SSH_PORT'])]
    env.host_url = _env['HOST']
    env.branch = _env['GIT_BRANCH']
    env.current_host = _env['CURRENT_HOST']
    env.env_name = env_name
    env.settings_module = _env['SETTINGS_MODULE']
    env.key_filename = _env['KEY_FILENAME']
    env.is_certbot_cert = _env.get('IS_CERTBOT_CERT')
    env.web_host = _env.get('WEBAPP_HOST', env.current_host)


@task
def create_non_priveledged_user():
    with settings(warn_only=True):
        sudo('adduser --disabled-login --gecos os {}'.format(DEPLOYMENT_USER))
        sudo('addgroup {}'.format(DEPLOYMENT_GROUP))
        sudo('adduser {user} {group}'
             .format(user=DEPLOYMENT_USER, group=DEPLOYMENT_GROUP))


@task
def prod():
    """
    Makes sure prod environment is enabled
    """
    _load_environment('PROD')


@task
def spa():
    _load_environment('SPA_PROD')


@task
def spa_qa():
    _load_environment('SPA_QA')


@task
def shell():
    os.execlp('ssh', '-C', '-i', env.key_filename, '%(user)s@%(host)s' % {'user': USER, 'host': env.HOST})


@task
def install_system_packages():
    # sudo('add-apt-repository ppa:fkrull/deadsnakes -y')
    sudo('add-apt-repository ppa:deadsnakes/ppa -y')

    if env.is_certbot_cert:
        sudo('add-apt-repository ppa:certbot/certbot -y')

    sudo('sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927')
    sudo('echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee '
         '/etc/apt/sources.list.d/mongodb-org-3.2.list')
    with settings(warn_only=True):
        sudo('apt-get update')

    if env.is_certbot_cert:
        sudo('apt-get -y --no-upgrade install %s' % ' '.join(UBUNTU_PACKAGES))
    else:
        UBUNTU_PACKAGES.remove('python-certbot-nginx')
        sudo('apt-get -y --no-upgrade install %s' % ' '.join(UBUNTU_PACKAGES))


@task
def checkout_repository():
    with cd(REMOTE_DEPLOY_DIR), settings(sudo_user=DEPLOYMENT_USER):
        # TODO: may be it is better to remove already
        # present directory
        if not exists(PROJECT_NAME, use_sudo=True):
            sudo('git clone %s %s' % (REPOSITORY, PROJECT_NAME))
            sudo('chown -R {user}:{group} {dir}'
                 .format(user=DEPLOYMENT_USER,
                         group=DEPLOYMENT_GROUP,
                         dir=PROJECT_NAME))


@task
def create_deploy_dirs():
    with cd(DEPLOY_DIR):
        sudo('mkdir -p staticfiles logs pid uploads',
             user=DEPLOYMENT_USER)


@task
def enable_and_start_redis():
    """
    Enable and starts redis server
    """
    sudo('systemctl enable redis-server')
    sudo('systemctl start redis-server')


@task
def prepare():
    install_system_packages()
    checkout_repository()
    create_deploy_dirs()
    prepare_virtualenv()
    create_database()
    enable_and_start_redis()

    if exists('/etc/nginx/sites-available/default'):
        with settings(warn_only=True):
            sudo('rm /etc/nginx/sites-available/default')


def add_virtualenv_settings_to_profile(profile_file):
    if not exists(profile_file):
        logger.info("Creating user profile: {}".format(profile_file))
        sudo('touch %s' % profile_file,
             user=DEPLOYMENT_USER)

    lines_to_append = [
        'export WORKON_HOME=%s' % WORKON_HOME,
        'export PROJECT_HOME=%s' % REMOTE_DEPLOY_DIR,
        'source /usr/local/bin/virtualenvwrapper.sh',
    ]

    for line in lines_to_append:
        if not contains(profile_file, line):
            append(profile_file, '\n' + line,
                   use_sudo=True)

    sudo('chown {user}:{group} {file}'
         .format(user=DEPLOYMENT_USER,
                 group=DEPLOYMENT_GROUP,
                 file=profile_file))


@task
def prepare_virtualenv():
    logger.info("Setting up the virtual environment.")
    sudo('pip install virtualenv')
    sudo('pip install virtualenvwrapper')

    add_virtualenv_settings_to_profile(USER_PROFILE_FILE)

    with prefix('source %s' % USER_PROFILE_FILE):
        with settings(warn_only=True), cd(REMOTE_DEPLOY_DIR):
            logger.info("Creating new virualenv.")
            sudo('mkvirtualenv %s -p /usr/bin/python3.5' % ENV_NAME,
                 user=DEPLOYMENT_USER)
    config_virtualenv()


@task
def config_virtualenv():
    remote_postactivate_path = os.path.join(WORKON_HOME, ENV_NAME,
                                            'bin/postactivate')
    postactivate_context = {
        'DATABASE_URL': DATABASE_URL,
        'SETTINGS_MODULE': env.settings_module,
        'IS_CERTBOT_CERT': env.is_certbot_cert,
        'DOMAIN_NAME': env.current_host,
    }
    upload_template(os.path.join(LOCAL_CONF_DIR, 'postactivate'),
                    remote_postactivate_path, context=postactivate_context,
                    use_sudo=True)


@task
def create_database():
    """
    Create postgres database and dedicated user
    """
    logger.info("Setting the database.")
    with settings(warn_only=True):
        # Create database user
        with prefix("export PGPASSWORD=%s" % DB_PASSWORD):
            sudo('psql -c "CREATE ROLE %s WITH CREATEDB CREATEUSER LOGIN ENCRYPTED PASSWORD \'%s\';"' % (
            DB_USER, DB_PASSWORD),
                 user='postgres')
            sudo('psql -c "CREATE DATABASE %s WITH OWNER %s"' % (DB_NAME, DB_USER),
                 user='postgres')


@task
def install_req():
    logger.info("Installing python requirements.")
    with cd(DEPLOY_DIR), prefix('source %s' % VENV_ACTIVATE):
        with settings(sudo_user=DEPLOYMENT_USER):
            cache_dir = os.path.join(DEPLOY_DIR, '.cache')
            sudo('pip install -U pip')
            # We avoid using cache as sometimes PIP does not
            # see new added requirements
            sudo('pip install --no-cache-dir -r {req_file}'
                 .format(cache=cache_dir, req_file='requirements.txt'))


@task
def deploy_files():
    with cd(DEPLOY_DIR), settings(sudo_user=DEPLOYMENT_USER):
        sudo('git fetch')
        sudo('git reset --hard')
        sudo('git checkout {}'.format(env.branch))
        sudo('git pull origin {}'.format(env.branch))


@task
def config_crontab():
    crontab_file = os.path.join(LOCAL_CONF_DIR, 'crontab')

    with settings(warn_only=True):
        # There may be no previous crontab so
        # crontab will fail
        backup_file = '/tmp/crontab-%s' % _get_current_datetime()
        logger.info("Backing up existing crontab")
        sudo('crontab -l > %s' % backup_file)
    logger.info("Uploading new crontab")
    put(crontab_file, '/tmp/new-crontab')
    logger.info("Setting new crontab")
    sudo('crontab < /tmp/new-crontab')


@task
def clean_pyc():
    """
    Cleans up redundant python bytecode files.
    """
    logger.info("Cleaning .pyc files.")
    with cd(DEPLOY_DIR):
        sudo("find . -name '*.pyc'")
        sudo('find . -name \*.pyc -delete')


@task
def migrate():
    with cd(DEPLOY_DIR):
        with settings(sudo_user=DEPLOYMENT_USER,
                      sudo_prefix=SUDO_PREFIX), prefix('workon steepshot_io'):
            sudo('python manage.py migrate')


def config_celery(remote_conf_path):
    """
    Copy celery related config files
    """
    require('settings_module')
    upload_template(os.path.join(LOCAL_CONF_DIR, 'celery.sh'),
                    remote_conf_path,
                    context={
                        'DEPLOY_DIR': DEPLOY_DIR,
                        'ENV_PATH': ENV_PATH,
                        'SETTINGS_MODULE': env.settings_module,
                    }, mode=0o0750, use_sudo=True)


def install_service(service_name, context):
    """
    Copies and enables specified systemd service
    to the remote server.
    """
    logger.info('Copying systemd services "%s"', service_name)
    remote_service = _get_systemd_service_path(service_name)
    local_template = os.path.join(LOCAL_CONF_DIR, service_name)
    if not os.path.exists(local_template):
        msg = 'Template "%s" does not exist.' % local_template
        logger.error(msg)
        raise ValueError(msg)
    upload_template(local_template,
                    remote_service,
                    context=context,
                    use_sudo=True,
                    backup=False)
    sudo('systemctl daemon-reload')
    # Autostart unit
    sudo('systemctl enable {}'.format(service_name))


@task
def install_systemd_services():
    services = (BACKEND_SERVICE, CELERY_SERVICE)
    common_context = {
        'PROJECT_NAME': PROJECT_NAME,
        'USER': DEPLOYMENT_USER,
        'GROUP': DEPLOYMENT_GROUP,
        'DEPLOY_DIR': DEPLOY_DIR,
    }
    for service in services:
        install_service(service, common_context)


@task
def deploy_nginx_config():
    require('host_url', 'env_name')
    remote_sa_path = '/etc/nginx/sites-available/%s' % PROJECT_NAME
    context = {
        'HOST': env.host_url,
        'CURRENT_HOST': env.current_host,
        'ENV': env.env_name,
        'DEPLOY_DIR': DEPLOY_DIR,
        'GUNI_PORT': GUNI_PORT,
        'STATIC_ROOT': STATIC_ROOT,
        'STATIC_URL': STATIC_URL,
        'MEDIA_ROOT': MEDIA_ROOT,
        'MEDIA_URL': MEDIA_URL
    }
    upload_template(template_dir=LOCAL_CONF_DIR,
                    filename='nginx.conf.j2',
                    destination=remote_sa_path,
                    context=context,
                    use_sudo=True,
                    use_jinja=True)
    sudo('ln -sf %s /etc/nginx/sites-enabled' % remote_sa_path)


@task
def config(restart_after=True):
    require('current_host', 'hosts', 'settings_module')
    # /etc/nginx/nginx.conf change user from www-data to root

    remote_conf_path = '%s/conf' % DEPLOY_DIR

    # remote_ssl_certificate_path = '/etc/ssl/certs'

    sudo('mkdir -p %s' % remote_conf_path,
         user=DEPLOYMENT_USER)
    GUNI_HOST = '0.0.0.0' if env.env_name == 'VAGRANT' else '127.0.0.1'

    upload_template(os.path.join(LOCAL_CONF_DIR, 'gunicorn.sh'), remote_conf_path, context={
        'DEPLOY_DIR': DEPLOY_DIR,
        'ENV_PATH': ENV_PATH,
        'SETTINGS_MODULE': env.settings_module,
        'GUNI_HOST': GUNI_HOST,
        'GUNI_PORT': GUNI_PORT,
        'GUNI_WORKERS': GUNI_WORKERS,
        'GUNI_TIMEOUT': GUNI_TIMEOUT,
        'GUNI_GRACEFUL_TIMEOUT': GUNI_GRACEFUL_TIMEOUT,
        'USER': DEPLOYMENT_USER,
        'GROUP': DEPLOYMENT_GROUP,
        'PROJECT_NAME': PROJECT_NAME
    }, mode=0o0750, use_sudo=True)

    config_celery(remote_conf_path)

    # TODO: replace it with systemd unit
    install_systemd_services()
    deploy_nginx_config()
    sudo('chown -R {}:{} {}'.format(DEPLOYMENT_USER, DEPLOYMENT_GROUP, remote_conf_path))
    # sudo('systemd daemon-reload')
    # path = os.path.join(LOCAL_CONF_DIR, 'ssl_certificate', 'www.steepshot.org.certchain.crt')
    # upload_template(path, remote_ssl_certificate_path, context={}, use_sudo=True),

    config_virtualenv()
    if restart_after:
        with settings(warn_only=True):
            restart()


def _is_systemd_service_running(service_name):
    with settings(warn_only=True):
        status_reply = sudo('systemctl --no-pager --full status %s'
                            % service_name)
        return 'inactive' not in status_reply


def restart_systemd_service(service_name):
    with settings(warn_only=True):
        if _is_systemd_service_running(service_name):
            sudo('systemctl stop %s' % service_name)
        sudo('systemctl start %s' % service_name)


@task
def restart():
    services_to_restart = [BACKEND_SERVICE,
                           CELERY_SERVICE]

    for service_name in services_to_restart:
        restart_systemd_service(service_name)

    sudo('service nginx restart')


@task
def restart_backend():
    sudo('systemctl stop %s' % BACKEND_SERVICE)
    sudo('systemctl start %s' % BACKEND_SERVICE)


@task
def restart_celery():
    sudo('systemctl stop %s' % CELERY_SERVICE)
    sudo('systemctl start %s' % CELERY_SERVICE)


@task
def check_status():
    services_to_check = [BACKEND_SERVICE,
                         CELERY_SERVICE]
    for service in services_to_check:
        sudo('systemctl --no-pager --full status %s' % service)


@task
def check_steepshot_service():
    sudo('systemctl --no-pager --full status %s' % BACKEND_SERVICE)


@task
def check_celery_service():
    sudo('systemctl --no-pager --full status %s' % CELERY_SERVICE)


@task
def deploy_static():
    """
    Collects django static files.
    """
    require('settings_module')
    with settings(sudo_user=DEPLOYMENT_USER,
                  sudo_prefix=SUDO_PREFIX), cd(DEPLOY_DIR):
        with prefix('workon %s' % ENV_NAME):
            sudo('python manage.py collectstatic --noinput --settings %s'
                 % env.settings_module)


@task
def update_static_chmod():
    sudo('chmod -R 664 %s' % STATIC_ROOT)
    sudo('chmod -R a+X %s' % STATIC_ROOT)
    sudo('chmod -R 664 %s' % MEDIA_ROOT)
    sudo('chmod -R a+X %s' % MEDIA_ROOT)


@task
def createsuperuser():
    require('settings_module')
    with settings(sudo_user=DEPLOYMENT_USER,
                  sudo_prefix=SUDO_PREFIX):
        with prefix('workon %s' % ENV_NAME):
            sudo('python manage.py createsuperuser '
                 '--settings ' + env.settings_module)


@task
def build_spa():
    if not os.path.exists(FRONTEND_LOCAL_DIR):
        logger.warning('Could not find repository '
                       'of the frontend application, '
                       'please clone it under the required '
                       'dir ("%s")', FRONTEND_LOCAL_DIR)
        sys.exit(1)
    # with lcd(FRONTEND_LOCAL_DIR):
        # perform_checkout = prompt('We are going to checkout the local frontend repository '
                                  # 'to the revision "{}". This may cause data loss, make '
                                  # 'sure you\'ve staged your uncommited changes. Checkout? (y/n)'
                                  # .format(env.branch),
                                  # validate=r'(y|n)',
                                  # default='n')
        # if perform_checkout.lower() == 'n':
            # logger.warning('Exiting.')
            # exit(1)
        # local('git fetch --all')
        # local('git reset --hard')
        # local('git checkout {}'.format(env.branch))
        # local('git pull origin {}'.format(env.branch))
        # local(FRONTEND_BUILD_COMMAND)


@task
def copy_spa():
    """
    Copies artifacts created
    after the front-end build
    """
    with lcd(FRONTEND_LOCAL_DIR):
        with settings(sudo_user=DEPLOYMENT_USER,
                      sudo_prefix=SUDO_PREFIX):
            put('dist/*', WEBAPP_STATIC_DIR)


@task
def deploy_spa_nginx_config():
    remote_sa_path = '/etc/nginx/sites-available/%s' % env.web_host
    context = {
        'WEBAPP_HOST': env.web_host,
        'ENV': env.env_name,
        'DEPLOY_DIR': DEPLOY_DIR,
        'STATIC_DIR': WEBAPP_STATIC_DIR,
    }
    upload_template(template_dir=LOCAL_CONF_DIR,
                    filename='web_app.nginx.conf.j2',
                    destination=remote_sa_path,
                    context=context,
                    use_sudo=True,
                    use_jinja=True,
                    backup=False)
    sudo('ln -sf %s /etc/nginx/sites-enabled' % remote_sa_path)
    sudo('service nginx restart')


@task
def deploy_spa():
    require('current_host', 'hosts')
    build_spa()
    copy_spa()
    deploy_spa_nginx_config()


@task
def first_time_deploy():
    """
    Call this task when deploying for the first time
    """
    create_non_priveledged_user()
    prepare()
    config()
    deploy()


@task
def deploy():
    require('branch', 'user', 'hosts')
    deploy_files()
    config_crontab()
    install_req()
    deploy_static()
    update_static_chmod()
    clean_pyc()
    migrate()
    install_systemd_services()
    restart()
