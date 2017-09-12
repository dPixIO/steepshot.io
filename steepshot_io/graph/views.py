import requests
from django.shortcuts import render
from django.views.generic import View
from steepshot_io.prod_settings import REQUESTS_URL_GOLOS, REQUESTS_URL_STEEM


class GetPostFee(View):
    template_name = 'fee_posts.html'

    def get_fee_posts(self, currency='VESTS'):

        res = requests.get(REQUESTS_URL_STEEM['post_fee'] + currency).json()
        res.reverse()
        values = []
        for i in res:
            values.append([i['day'], i['count_fee']])
        return values

    def get(self, request, *args, **kwargs):
        if 'currency' in request.GET:
            currency = request.GET['currency'].lower()
            values = self.get_fee_posts(currency)
        else:
            values = self.get_fee_posts()
        return render(request, self.template_name, {'values': values})


class GetPostsCountMonthly(View):
    template_name = 'count_posts.html'

    def group_steem_golos(self, list_steem, list_golos):
        res = []
        idx = 0
        while True:
            try:
                res.append([list_steem[idx][0], list_steem[idx][1] + list_golos[idx][1]])
            except IndexError:
                break
            idx += 1
        return res

    def get_posts_count_monthly(self, platform=None):

        if platform == 'steem':
            res = requests.get(REQUESTS_URL_STEEM['posts_count_monthly']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['posts_count']])
            return values
        elif platform =='golos':
            res = requests.get(REQUESTS_URL_GOLOS['posts_count_monthly']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['posts_count']])
            return values
        else:
            res_steem = requests.get(REQUESTS_URL_STEEM['posts_count_monthly']).json()
            res_steem.reverse()
            res_golos = requests.get(REQUESTS_URL_GOLOS['posts_count_monthly']).json()
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i['date_to'], i['posts_count']])
            for i in res_golos:
                values_golos.append([i['date_to'], i['posts_count']])
            steem_golos_value = self.group_steem_golos(values_steem, values_golos)

            return steem_golos_value

    def get(self, request):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_posts_count_monthly(platform=platform)
        else:
            values = self.get_posts_count_monthly()
        return render(request, self.template_name, {'values': values})


class GetActiveUsers(GetPostsCountMonthly):
    template_name = 'active_users.html'

    def get_active_users(self, platform=None):
        if platform == 'steem':
            res = requests.get(REQUESTS_URL_STEEM['active_users']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['active_users']])
            return values
        elif platform == 'golos':
            res = requests.get(REQUESTS_URL_GOLOS['active_users']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['active_users']])
            return values

        else:
            res_steem = requests.get(REQUESTS_URL_STEEM['active_users']).json()
            res_steem.reverse()
            res_golos = requests.get(REQUESTS_URL_GOLOS['active_users']).json()
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i['date_to'], i['active_users']])
            for i in res_golos:
                values_golos.append([i['date_to'], i['active_users']])

            steem_golos_value = self.group_steem_golos(values_steem, values_golos)

            return steem_golos_value

    def get(self, request):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_active_users(platform=platform)
        else:
            values = self.get_active_users()
        return render(request, self.template_name, {'values': values})


class GetCountPostDaily(View):
    template_name = 'count_post_daily.html'

    def get_count_post_daily(self):
        res = requests.get(REQUESTS_URL_STEEM['posts_count_daily']).json()
        res.reverse()
        values = []
        for i in res:
            values.append([i['day'], i['count_posts']])
        return values

    def get(self, request):
        values = self.get_count_post_daily()
        return render(request, self.template_name, {'values': values})


class GetRatioDaily(View):
    template_name = 'ratio_daily.html'

    def group_steem_golos(self, list_steem, list_golos):
        res = []
        idx = 0
        while True:
            try:
                res.append([list_steem[idx][0], list_steem[idx][1], list_golos[idx][1]])
            except IndexError:
                break
            idx += 1
        return res

    def get_ratio_daily(self, platform=None):

        if platform == 'steem':
            res = requests.get(REQUESTS_URL_STEEM['ration_daily']).json()
            res = res['result']
            res.reverse()
            values = []
            for i in res:
                values.append([i['date'], i['ratio']])
            return values
        elif platform == 'golos':
            res = requests.get(REQUESTS_URL_GOLOS['ration_daily']).json()
            res = res['result']
            res.reverse()
            values = []
            for i in res:
                values.append([i['date'], i['ratio']])
            return values
        else:
            res_steem = requests.get(REQUESTS_URL_STEEM['ration_daily']).json()
            res_steem = res_steem['result']
            res_steem.reverse()
            res_golos = requests.get(REQUESTS_URL_GOLOS['ration_daily']).json()
            res_golos = res_golos['result']
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i['date'], i['ratio']])
            for i in res_golos:
                values_golos.append([i['date'], i['ratio']])
            return values_steem, values_golos

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_ratio_daily(platform=platform)
            return render(request, self.template_name, {'values': values})

        else:
            values_steem, values_golos = self.get_ratio_daily()
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class GetRatioMonthly(GetRatioDaily):
    template_name = 'ratio_monthly.html'

    def get_ratio_monthly(self, platform=None):

        if platform == 'steem':
            res = requests.get(REQUESTS_URL_STEEM['ration_monthly']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['ratio']])
            return values
        elif platform == 'golos':
            res = requests.get(REQUESTS_URL_GOLOS['ration_monthly']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['ratio']])
            return values
        else:
            res_steem = requests.get(REQUESTS_URL_STEEM['ration_monthly']).json()
            res_steem.reverse()
            res_golos = requests.get(REQUESTS_URL_GOLOS['ration_monthly']).json()
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i['date_to'], i['ratio']])
            for i in res_golos:
                values_golos.append([i['date_to'], i['ratio']])
            return values_steem, values_golos

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_ratio_monthly(platform=platform)
            return render(request, self.template_name, {'values': values})

        else:
            values_steem, values_golos = self.get_ratio_monthly()
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})



class CoutNewUsers(GetRatioDaily):
    template_name = 'stats_users.html'

    def _get_data(self, platform=None, url=None, data_x=None, data_y=None, reverce=True):
        if platform == 'steem':
            res = requests.get(REQUESTS_URL_STEEM[url]).json()
            if reverce:
                res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        elif platform == 'golos':
            res = requests.get(REQUESTS_URL_GOLOS[url]).json()
            if reverce:
                res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        else:
            res_steem = requests.get(REQUESTS_URL_STEEM[url]).json()
            if reverce:
                res_steem.reverse()
            res_golos = requests.get(REQUESTS_URL_GOLOS[url]).json()
            if reverce:
                res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i[data_x], i[data_y]])
            for i in res_golos:
                values_golos.append([i[data_x], i[data_y]])
            return values_steem, values_golos

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='new_users', data_x='day', data_y='count_users', reverce=False)
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='new_users', data_x='day', data_y='count_users', reverce=False)
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class CoutNewUsersMonthly(CoutNewUsers):

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='new_users_monthly', data_x='date_to', data_y='count_new_users')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='new_users_monthly', data_x='date_to', data_y='count_new_users')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class CoutPercentUsersDaily(CoutNewUsers):
    template_name = 'percent_users.html'

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_data(platform=platform, url='users_percent_daily', data_x='day', data_y='percent', reverce=False)
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self.get_data(url='users_percent_daily', data_x='day', data_y='percent', reverce=False)
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class CountPostWeekly(CoutNewUsers):
    template_name = 'count_posts_weekly.html'

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='count_posts_weekly', data_x='day', data_y='count_post')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='count_posts_weekly', data_x='day', data_y='count_post')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})

class PostsAverageWeekly(CountPostWeekly):

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='posts_average_weekly', data_x='day', data_y='count_post')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='posts_average_weekly', data_x='day', data_y='count_post')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class PostsAverageAuthor(CountPostWeekly):

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='posts_average_author', data_x='day', data_y='count_posts')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='posts_average_author', data_x='day', data_y='count_posts')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class CountVotesWeekly(CountPostWeekly):
    template_name = 'count_posts_weekly.html'

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='count_votes_weekly', data_x='day', data_y='count_votes')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='count_votes_weekly', data_x='day', data_y='count_votes')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class AverageVotesWeekly(CountVotesWeekly):
    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='votes_average_weekly', data_x='day', data_y='votes_count')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='votes_average_weekly', data_x='day', data_y='votes_count')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class CountCommentsWeekly(CountPostWeekly):
    template_name = 'count_comments.html'

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='count_comments_weekly', data_x='day', data_y='count_comments')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='count_comments_weekly', data_x='day', data_y='count_comments')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class CountUsersSessions(CountPostWeekly):
    template_name = 'count_sessions.html'

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url='users_count_session', data_x='day', data_y='count_sessions')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='users_count_session', data_x='day', data_y='count_sessions')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class PostsFeeWeekly(CountPostWeekly):
    template_name = 'posts_fee_weekly.html'

    def get(self, request, *args, **kwargs):
        current_url = request.resolver_match.url_name
        import pdb
        pdb.set_trace()
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url=current_url, data_x='day', data_y='fee')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url=current_url, data_x='day', data_y='fee')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})
