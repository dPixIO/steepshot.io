from django.core.management import BaseCommand

from steepshot_io.core import tasks


class Command(BaseCommand):
    help = "Get cert expiration date"

    def handle(self, *args, **options):
        tasks.check_cert_expiration_date.delay()
