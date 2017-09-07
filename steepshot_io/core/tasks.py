import os
import ssl
import subprocess
from datetime import datetime, timedelta
from ssl import SSLError, SSLZeroReturnError, SSLEOFError, CertificateError

import OpenSSL
import dateutil.parser
from celery import task


@task()
def check_cert_expiration_date():
    # WARNING: The user from which this task is launched should be added to the sudoers.
    # For example:
    # <username> ALL = (ALL:ALL) NOPASSWD: /bin/systemctl stop nginx.service
    # <username> ALL = (ALL:ALL) NOPASSWD: /bin/systemctl start nginx.service
    # <username> ALL = (ALL:ALL) NOPASSWD: /usr/bin/certbot renew

    django_certbot_cert = os.getenv('DJANGO_CERTBOT_CERT')
    if django_certbot_cert == 'False' or django_certbot_cert is None:
        print("CertBot certificate not used!")
        return
    elif django_certbot_cert == 'True':
        def get_days_left():
            try:
                cert = ssl.get_server_certificate((os.getenv('DJANGO_DOMAIN'), 443))
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
                days_left = dateutil.parser.parse(x509.get_notAfter()).date() - datetime.now().date()
                return days_left
            except (SSLError, SSLEOFError,
                    SSLZeroReturnError, CertificateError,
                    ConnectionAbortedError, ConnectionError,
                    ConnectionRefusedError, ConnectionResetError) as e:
                print('Got the following error during to get server certificate: {error}'.format(error=e))
                return timedelta(days=100)

        if get_days_left() < timedelta(days=7):
            print("Certificate will expire soon! Performing certificate renewal.")

            nginx_process = subprocess.run(['sudo', 'systemctl', 'stop', 'nginx.service'],
                                           stdout=subprocess.PIPE)
            if nginx_process.returncode != 0:
                print("Nginx service has not been stopped successfully!")
                print(nginx_process.stdout)
                return

            certbot_process = subprocess.run(['sudo', 'certbot', 'renew'],
                                             stdout=subprocess.PIPE)
            if certbot_process.returncode == 0:
                print("Certificate has been renewed!")
                print("{days} days left when certificate will expire.".format(days=get_days_left().days))
            else:
                print("Certificate has not been renewed for reason below!")
                print(certbot_process.stdout)

            nginx_process = subprocess.run(['sudo', 'systemctl', 'start', 'nginx.service'],
                                           stdout=subprocess.PIPE)

            if nginx_process.returncode != 0:
                print("Nginx service has not been started successfully!")
                print(nginx_process.stdout)
                return

            print("The 'check_cert_expiration_date' task has been successfully completed!")
        else:
            print("{days} days left when certificate will expire.".format(days=get_days_left().days))
