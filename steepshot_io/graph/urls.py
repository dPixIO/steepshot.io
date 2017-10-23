from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^comments/count$', CommentsCount.as_view(), name='count_comments_weekly'),
    url(r'^posts/average/author$', PostsAverageAuthor.as_view(), name='posts_average_author'),
    url(r'^posts/count/monthly$', PostsCountMonthly.as_view(), name='count_posts'),
    url(r'^posts/count/daily$', PostsCountDaily.as_view(), name='count_posts_daily'),
    url(r'^posts/fee/curator$', PostsFeeCurator.as_view(), name='posts_fee_weekly'),
    url(r'^posts/fee/daily$', PostsFee.as_view(), name='posts_fee_weekly'),
    url(r'^posts/fee/users$', PostsFeeUsers.as_view(), name='posts_fee_users'),
    url(r'^posts/fee/author$', PostsFeeAuthor.as_view(), name='posts_fee_author'),
    url(r'^posts/ratio/daily$', PostsRatioDaily.as_view(), name='ratio_daily'),
    url(r'^posts/ratio/monthly$', PostsRatioMonthly.as_view(), name='ratio_monthly'),
    url(r'^users/active$', UsersActive.as_view(), name='active_users'),
    url(r'^users/count/sessions$', CountUsersSessions.as_view(), name='users_count_session'),
    url(r'^users/new/daily$', UsersNewCountDaily.as_view(), name='new_users'),
    url(r'^users/new/monthly$', UsersNewCountMonthly.as_view(), name='new_users'),
    url(r'^users/percent/daily$', UsersCountPercentDaily.as_view(), name='percent_users'),
    url(r'^votes/average$', AverageVotes.as_view(), name='votes_average_weekly'),
    url(r'^votes/count$', VotesCount.as_view(), name='count_votes_weekly'),
]
