from datetime import datetime
from django.conf import settings


def str_from_datetime(date_str: datetime) -> str:
    return datetime.strftime(date_str, settings.DEFAULT_DATE_FORMAT)
