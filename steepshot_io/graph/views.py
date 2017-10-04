import requests
import logging
from django.shortcuts import render
from django.views.generic import View
from django.conf import settings


logger = logging.getLogger(__name__)


class GetPostFee(View):
    template_name = 'fee_posts.html'

    def _get_data(self, currency='VESTS', name_key=None, name_url=None, use_fee=True):
        try:
            if not use_fee:
                currency = ''
            res = requests.get(settings.REQUESTS_URL_STEEM[name_url] + currency).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['day'], i[name_key]])
        except Exception as e:
            logger.error(e)
            values = []
        return values

    def get(self, request, *args, **kwargs):
        if 'currency' in request.GET:
            currency = request.GET['currency'].lower()
            values = self._get_data(currency=currency, name_key='count_fee', name_url='post_fee')
        else:
            values = self._get_data(name_key='count_fee', name_url='post_fee')
        name = 'fee in day'
        return render(request, self.template_name, {'values': values, 'name_1': name})


class GetPostsCountMonthly(View):
    template_name = 'fee_posts.html'

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

    def _get_data(self, platform=None, reverse=True, data_x=None, data_y=None, name_url=None):
        if platform == 'steem':
            try:
                res = requests.get(settings.REQUESTS_URL_STEEM[name_url]).json()
            except Exception as e:
                logger.error(e)
                res = []
                return res
            if reverse:
                res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        elif platform =='golos':
            try:
                res = requests.get(settings.REQUESTS_URL_GOLOS[name_url]).json()
            except Exception as e:
                logger.error(e)
                res = []
                return res
            if reverse:
                res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        else:
            try:
                res_steem = requests.get(settings.REQUESTS_URL_STEEM[name_url]).json()
                res_golos = requests.get(settings.REQUESTS_URL_GOLOS[name_url]).json()
            except Exception as e:
                logger.error(e)
                res = []
                return res
            if reverse:
                res_steem.reverse()
                res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i[data_x], i[data_y]])
            for i in res_golos:
                values_golos.append([i[data_x], i[data_y]])
            steem_golos_value = self.group_steem_golos(values_steem, values_golos)
            return steem_golos_value

    def get(self, request):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, name_url='posts_count_monthly', data_y='posts_count', data_x='date_to')
        else:
            values = self._get_data(name_url='posts_count_monthly', data_y='posts_count', data_x='date_to')
        name = 'counts posts'
        return render(request, self.template_name, {'values': values, 'name_1': name})


class GetActiveUsers(GetPostsCountMonthly):
    def get(self, request):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, name_url='active_users', data_y='active_users', data_x='date_to')
        else:
            values = self._get_data(name_url='active_users', data_y='active_users', data_x='date_to')
        name = 'active users'
        return render(request, self.template_name, {'values': values, 'name_1': name})


class GetCountPostDaily(GetPostFee):
    def get(self, request, *args, **kwargs):
        values = self._get_data(use_fee=False, name_url='posts_count_daily', name_key='count_posts')
        name = 'count posts'
        return render(request, self.template_name, {'values': values, 'name_1': name})


class GetRatioDaily(View):
    template_name = 'fee_posts.html'

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

    def _get_data(self, platform=None, reverse=True, data_x=None, data_y=None, name_url=None):
        if platform == 'steem':
            res = requests.get(settings.REQUESTS_URL_STEEM[name_url]).json()
            res = res['result']
            res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        elif platform == 'golos':
            res = requests.get(settings.REQUESTS_URL_GOLOS[name_url]).json()
            res = res['result']
            res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        else:
            res_steem = requests.get(settings.REQUESTS_URL_STEEM[name_url]).json()
            res_steem = res_steem['result']
            res_steem.reverse()
            res_golos = requests.get(settings.REQUESTS_URL_GOLOS[name_url]).json()
            res_golos = res_golos['result']
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
            name_1 = 'ratio ' + platform
            values = self._get_data(platform=platform, data_y='ratio', name_url='ration_daily', data_x='date')
            return render(request, self.template_name, {'values': values, 'name_1': name_1})

        else:
            name_1 = 'ratio steem'
            name_2 = 'ratio golos'
            values_steem, values_golos = self._get_data(data_y='ratio', name_url='ration_daily', data_x='date')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together, 'name_1': name_1, 'name_2': name_2})


class GetRatioMonthly(GetRatioDaily):
    template_name = 'ratio_monthly.html'

    def get_ratio_monthly(self, platform=None):

        if platform == 'steem':
            res = requests.get(settings.REQUESTS_URL_STEEM['ration_monthly']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['ratio']])
            return values
        elif platform == 'golos':
            res = requests.get(settings.REQUESTS_URL_GOLOS['ration_monthly']).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['ratio']])
            return values
        else:
            res_steem = requests.get(settings.REQUESTS_URL_STEEM['ration_monthly']).json()
            res_steem.reverse()
            res_golos = requests.get(settings.REQUESTS_URL_GOLOS['ration_monthly']).json()
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
            res = requests.get(settings.REQUESTS_URL_STEEM[url]).json()
            if reverce:
                res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        elif platform == 'golos':
            res = requests.get(settings.REQUESTS_URL_GOLOS[url]).json()
            if reverce:
                res.reverse()
            values = []
            for i in res:
                values.append([i[data_x], i[data_y]])
            return values
        else:
            res_steem = requests.get(settings.REQUESTS_URL_STEEM[url]).json()
            if reverce:
                res_steem.reverse()
            res_golos = requests.get(settings.REQUESTS_URL_GOLOS[url]).json()
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
            values = self._get_data(platform=platform, url='users_percent_daily', data_x='day', data_y='percent', reverce=False)
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url='users_percent_daily', data_x='day', data_y='percent', reverce=False)
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
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self._get_data(platform=platform, url=current_url, data_x='day', data_y='fee')
            return render(request, self.template_name, {'values': values})
        else:
            values_steem, values_golos = self._get_data(url=current_url, data_x='day', data_y='fee')
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})
