from datetime import datetime
from django.conf import settings


def group_data(list_1, list_2):
    date_my = list_1[0]
    x = list_1[1][1:]
    y = list_2[1][1:]
    sum_list = list(map(lambda a, b: a + b, x, y))
    sum_list.insert(0, date_my)
    return date_my, sum_list


def str_from_datetime(date_str: datetime) -> str:
    return datetime.strftime(date_str, settings.DEFAULT_DATE_FORMAT)
