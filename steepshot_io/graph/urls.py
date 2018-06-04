from django.conf.urls import url

from .views import *  # noqa

urlpatterns = [
    url(r'^logout$', Logout.as_view(), name='logout'),
    url(r'^all/stats$', GetAllStats.as_view(), name='all_stats'),
    url(r'^users/active$', UsersActive.as_view(), name='active_users_monthly'),
    url(r'^users/sessions$', UserSessions.as_view(), name='user_sessions_daily'),
    url(r'^users/new/daily$', UsersNewCountDaily.as_view(), name='new_users_daily'),
    url(r'^users/new/monthly$', UsersNewCountMonthly.as_view(), name='new_users_monthly'),
    url(r'^users/percent/daily$', UsersCountPercentDaily.as_view(), name='new_users_percent_daily'),

    url(r'^users/active/daily$', GetDAU.as_view(), name='DAU'),
    url(r'^users/active/new$', GetDAUNewUsers.as_view(), name='DAU_new_users'),

    url(r'^posts/average/author$', PostsAverageAuthor.as_view(), name='posts_average_per_author'),
    url(r'^posts/count/monthly$', PostsCountMonthly.as_view(), name='count_posts'),
    url(r'^posts/count/daily$', PostsCountDaily.as_view(), name='count_posts_daily'),
    url(r'^posts/count/new/users$', GetPostsCountNewUsers.as_view(), name='posts_count_new_users'),
    url(r'^posts/fee/daily$', PostsFeeDaily.as_view(), name='posts_fee_daily'),
    url(r'^posts/payout/users$', GetUserPayout.as_view(), name='posts_payout_users'),
    url(r'^posts/fee/weekly$', PostsFeeWeekly.as_view(), name='posts_fee_weekly'),
    url(r'^posts/fee/users$', AverageFeePerUserSession.as_view(), name='posts_fee_users'),
    url(r'^posts/fee/author$', AverageFeePerAuthor.as_view(), name='posts_fee_author'),
    url(r'^posts/ratio/daily$', PostsRatioDaily.as_view(), name='ratio_daily'),
    url(r'^posts/ratio/monthly$', PostsRatioMonthly.as_view(), name='ratio_monthly'),
    url(r'^posts/sharing$', PostsSharing.as_view(), name='posts_sharing'),

    url(r'^timeouts/daily$', GetDailyTimeouts.as_view(), name='timeouts_daily'),
    url(r'^stats/ltv$', GetLtvDaily.as_view(), name='ltv_daily'),
    url(r'^stats/total_active_power_daily$', GetTotalActivePowerDaily.as_view(), name='total_active_power_daily'),

    url(r'^comments/count$', CommentsCount.as_view(), name='count_comments_weekly'),
    url(r'^comments/percentage$', CommentsPercentage.as_view(), name='comments_percentage'),

    url(r'^browse/request/count$', GetHotTopNewCount.as_view(), name='count_requests'),

    url(r'^browse/request/users$', GetBrowseUsersCount.as_view(), name='browse_users_request'),

    url(r'^votes/average$', AverageVotes.as_view(), name='votes_average_weekly'),

    url(r'^votes/count/daily$', VotesCountDaily.as_view(), name='count_votes_daily'),
    url(r'^votes/count/monthly$', VotesCountMonthly.as_view(), name='count_votes_monthly'),

    url(r'^coolness/requests$', CoolnessRequests.as_view(), name='coolness_requests'),
    url(r'^steepshot-votes$', SteepshotVotes.as_view(), name='steepshot_votes'),
]
