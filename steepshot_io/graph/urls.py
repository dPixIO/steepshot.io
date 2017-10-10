from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^posts/count/monthly$', GetPostsCountMonthly.as_view(), name='count_posts'),
    url(r'^posts/count/daily$', GetCountPostDaily.as_view(), name='count_posts_daily'),
    url(r'^posts/ratio/daily$', GetRatioDaily.as_view(), name='ratio_daily'),
    url(r'^posts/ratio/monthly$', GetRatioMonthly.as_view(), name='ratio_monthly'),
    url(r'^posts/currency/fee$', GetPostFee.as_view(), name='posts_fee'),
    url(r'^active/users$', GetActiveUsers.as_view(), name='active_users'),
    url(r'^new/users/daily$', CoutNewUsers.as_view(), name='new_users'),
    url(r'^new/users/monthly$', CoutNewUsersMonthly.as_view(), name='new_users'),
    url(r'^users/percent/daily$', CoutPercentUsersDaily.as_view(), name='percent_users'),
    url(r'^posts/count/weekly$', CountPostWeekly.as_view(), name='count_posts_weekly'),
    # url(r'^posts/average/weekly$', PostsAverageWeekly.as_view(), name='posts_average_weekly'),
    url(r'^posts/average/author$', PostsAverageAuthor.as_view(), name='posts_average_author'),
    url(r'^count/votes/weekly$', CountVotesWeekly.as_view(), name='count_votes_weekly'),
    # url(r'^votes/average/weekly$', AverageVotesWeekly.as_view(), name='votes_average_weekly'),
    url(r'^count/comments/weekly$', CountCommentsWeekly.as_view(), name='count_comments_weekly'),
    # url(r'^count/users/sessions$', CountUsersSessions.as_view(), name='users_count_session'),
    url(r'^posts/fee/weekly$', PostsFeeWeekly.as_view(), name='posts_fee_weekly'),
    # url(r'^posts/fee/users$', PostsFeeWeekly.as_view(), name='posts_fee_users'),
    url(r'^posts/fee/author$', PostsFeeWeekly.as_view(), name='posts_fee_author'),


]
