from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^stats$', GetStatsTable.as_view(), name='stats_table'),
    url(r'^delegators$', GetDelegatorsDPix.as_view(), name='delegators_table'),
    url(r'^instagram$', InstagramTableStatsView.as_view(), name='instagram_table'),
]
