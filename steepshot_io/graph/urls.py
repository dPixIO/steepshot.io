from django.conf.urls import url

from .views import GetPostFee, GetActiveUsers, GetPostsCountMonthly

urlpatterns = [
    url(r'^posts/count$', GetPostsCountMonthly.as_view(), name='count_posts'),
    url(r'^posts/fee', GetPostFee.as_view(), name='posts_fee'),
    url(r'^active/users$', GetActiveUsers.as_view(), name='active_users'),
]
