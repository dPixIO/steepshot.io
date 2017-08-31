from django.conf.urls import url

from .views import IndexView, GetFAQ

urlpatterns = [
    url(r'^faq', GetFAQ.as_view(), name='faq'),
    url(r'^$', IndexView.as_view(), name='index'),
]
