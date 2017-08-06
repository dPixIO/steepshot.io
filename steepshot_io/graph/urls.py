from django.conf.urls import url

from .views import GetPostFee, GetActiveUsers, GetPostsCountMonthly, GetCountPostDaily, GetRatioDaily, GetRatioMonthly

urlpatterns = [
    url(r'^posts/count/monthly$', GetPostsCountMonthly.as_view(), name='count_posts'),
    url(r'^posts/count/daily$', GetCountPostDaily.as_view(), name='count_posts_daily'),
    url(r'^posts/ratio/daily$', GetRatioDaily.as_view(), name='ratio_daily'),
    url(r'^posts/ratio/monthly$', GetRatioMonthly.as_view(), name='ratio_monthly'),
    url(r'^posts/fee', GetPostFee.as_view(), name='posts_fee'),
    url(r'^active/users$', GetActiveUsers.as_view(), name='active_users'),
]
