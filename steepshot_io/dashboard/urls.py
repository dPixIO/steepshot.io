from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', GetDashboard.as_view(), name='dashboard_stats'),
]