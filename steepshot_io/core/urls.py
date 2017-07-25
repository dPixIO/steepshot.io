from django.conf import settings
from django.conf.urls import url
from django.contrib import admin

from .views import IndexView, GetPostFee, GetActiveUsers, GetPostsCountMonthly

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^graph/posts/count$', GetPostsCountMonthly.as_view(), name='count_posts'),
    url(r'^graph/posts/fee', GetPostFee.as_view(), name='posts_fee'),
    url(r'^graph/active/users$', GetActiveUsers.as_view(), name='active_users'),
]
