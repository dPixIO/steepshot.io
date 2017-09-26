from django.conf.urls import url

from .views import IndexView, GetFAQ, GetTeam
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^faq$', GetFAQ.as_view(), name='faq'),
    url(r'^team$', GetTeam.as_view(), name='team'),
    url(r'^$', IndexView.as_view(), name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
