from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^stats$', GetStatsTable.as_view(), name='stats_table'),
]