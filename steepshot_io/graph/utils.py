from datetime import date, datetime, timedelta

from django.conf import settings


def extract_date_in_default_format(date_string: str) -> date:
    return datetime.strptime(date_string,
                             settings.DEFAULT_DATE_FORMAT).date()


def default_date_format(date: date) -> str:
    return date.strftime(settings.DEFAULT_DATE_FORMAT)


def get_date_range_from_request(request, day_difference: int=30) -> dict:
    """
    Extract date range parameters from the request if any.
    """
    date_to = request.GET.get('date_to')
    if date_to:
        date_to = extract_date_in_default_format(date_to)
    else:
        date_to = date.today() - timedelta(days=1)
    date_from = date_to - timedelta(days=day_difference)
    return {'date_from': default_date_format(date_from),
            'date_to': default_date_format(date_to)}
