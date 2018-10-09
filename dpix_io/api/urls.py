from django.conf.urls import url, include

from dpix_io.api import views

urlpatterns = [
    url(r'^v1/', include([
        url(r'^work-request$', views.WorkRequestAPIView.as_view(), name='work_request')
    ]), name='api_v1'),
]
