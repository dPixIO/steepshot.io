from django.conf.urls import url

from .views import IndexView, GetFAQ, GetTeam, GetJobs, GetJob, GetInvestor, PostAnalitycs
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^faq$', GetFAQ.as_view(), name='faq'),
    url(r'^team$', GetTeam.as_view(), name='team'),
    url(r'^jobs$', GetJobs.as_view(), name='jobs'),
    url(r'^job/(\d+)$', GetJob.as_view(), name='job_one'),
    url(r'^investors$', GetInvestor.as_view(), name='investors'),
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^post-analitycs$', PostAnalitycs.as_view(), name='post_analitycs'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
