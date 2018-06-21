import logging
from enum import Enum
from json.decoder import JSONDecodeError
from typing import Dict
import requests
from requests.exceptions import HTTPError, ConnectionError
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.http import JsonResponse

from steepshot_io.graph.data_modifiers import SumModifier, AverageModifier, BaseModifier
from steepshot_io.graph.utils import get_date_range_from_request, default_date_format
from steepshot_io.dashboard.forms import UserLoginDasboardForm


logger = logging.getLogger(__name__)


class ApiUrls(Enum):
    steem = 'steem'
    golos = 'golos'


class Logout(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('core:index'))


class BaseView(View):
    template_name = 'graph.html'
    title = ''
    subtitle = ''
    template_login = 'stats_login.html'

    def fetch_data(self,
                   apis=None,
                   api_query=None,
                   name_url=None,
                   modifiers=None,
                   data_x=None,
                   data_y=None) -> Dict:
        all_endpoint_urls = {
            ApiUrls.steem: settings.REQUESTS_URL.get(name_url, '{url}').format(url=settings.STEEM_V1),
            ApiUrls.golos: settings.REQUESTS_URL.get(name_url, '{url}').format(url=settings.GOLOS_V1)
        }

        res = {
            'headers': [
                {'Date': 'string'}
            ],
            'data': []
        }
        if not apis:
            apis = ApiUrls
        elif isinstance(apis, ApiUrls):
            apis = [apis]

        if not api_query:
            months = 3
            days = 30
            date_to = date.today()
            date_from = date_to - timedelta(days=days * months)
            api_query = {
                'date_from': date_from,
                'date_to': date_to
            }

        for i in apis:
            res['headers'].extend([{i.value.capitalize(): 'number'}])

        res_data_idx_map = {}

        for i, api in enumerate(apis, start=1):
            try:
                data = requests.get(all_endpoint_urls.get(api), params=api_query).json()
                if 'result' in data:
                    data = data['result']
            except JSONDecodeError as e:
                logger.error('Failed to parse json: {err}.'.format(err=e))
                continue
            except (ConnectionError, HTTPError) as e:
                logger.error('Failed to connect to {platform} server: {err}.'.format(platform=api.value, err=e))
                continue
            except Exception as e:
                logger.error('Unexpected error: {err}'.format(err=e))
                continue

            for d in data:
                key = d.get(data_x)
                res_data_idx = res_data_idx_map.get(key)
                if res_data_idx is None:
                    res_data_idx = len(res['data'])
                    res_data_idx_map[key] = res_data_idx
                    res['data'].append([key] + [0 for i in apis])
                if 'ltv' in d:
                    res['data'][res_data_idx][i] = d['ltv'].get(data_y)
                else:
                    res['data'][res_data_idx][i] = d.get(data_y)

        res['data'] = sorted(res['data'], key=lambda x: x[0])

        if res['data'] and len(apis) > 1 and modifiers:
            if not isinstance(modifiers, list):
                modifiers = [modifiers]
            for modifier in modifiers:
                if BaseModifier in modifier.__bases__:
                    modifier.modify(res, len(apis))
        return res

    def get_data(self) -> Dict:
        pass

    def post(self, request, *args, **kwargs):
        form = UserLoginDasboardForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username,  password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(request.POST['next_path'])
                else:
                    messages.error(request, 'You are banned')
            else:
                messages.error(request, 'Incorrect username or password')
        return render(request, self.template_login, {'form': form})

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated() and request.method == 'GET':
            next_path = request.path
            form = UserLoginDasboardForm()
            return render(request, self.template_login, {'form': form, 'next_path': next_path})
        return super(BaseView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        data = self.get_data()
        data.update({
            'title': self.title,
            'subtitle': self.subtitle
        })
        return render(request, self.template_name, data)


class UsersActive(BaseView):
    """
    MAU for the last month (30 days). MAU - monthly active users.
    MAU for today is calculated the following way (from -30 to 0 day)
    GET param:
        date_to = default date (yesterday)
        date_from = default 30 days ago
        user_agent = default (all)
    """


    title = 'Monthly active users'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='active_users_monthly',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='date_to',
            data_y='active_users'
        )


class UserSessions(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """

    title = 'User sessions count'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='user_sessions_daily',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='day',
            data_y='count_sessions'
        )


class UsersNewCountDaily(BaseView):
    title = 'New users count'
    subtitle = 'Daily count of new users'

    def get_data(self):
        return self.fetch_data(
            name_url='new_users_daily',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='day',
            data_y='count_users'
        )


class UsersNewCountMonthly(BaseView):
    title = 'New users count'
    subtitle = 'Monthly count of new users'

    def get_data(self):
        return self.fetch_data(
            name_url='new_users_monthly',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='date_to',
            data_y='count_new_users'
        )


class UsersCountPercentDaily(BaseView):
    title = 'Users percent daily'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='new_users_percent_daily',
            api_query=self.request.GET,
            modifiers=AverageModifier,
            data_x='day',
            data_y='percent'
        )


class PostsAverageAuthor(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """

    title = 'Posts average per author'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_average_per_author',
            api_query=self.request.GET,
            modifiers=AverageModifier,
            data_x='day',
            data_y='count_posts'
        )


class PostsCountMonthly(BaseView):
    title = 'Posts count monthly'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_count_monthly',
            modifiers=SumModifier,
            data_x='date_to',
            data_y='posts_count'
        )


class PostsCountDaily(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """

    title = 'Posts count daily'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_count_daily',
            data_x='day',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_y='count_posts'
        )


class PostsFeeDaily(BaseView):
    """
    Curator rewards
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """

    title = 'Benefeciary payout'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            apis=ApiUrls.steem,
            api_query=self.request.GET,
            modifiers=SumModifier,
            name_url='posts_fee_daily',
            data_x='day',
            data_y='total_payout_per_day'
        )


class PostsFeeWeekly(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
        currency =  (SBD, steem, usd) defauld SBD
    """

    title = 'Posts fee weekly'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_fee_weekly',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='date_to',
            data_y='fee'
        )


class AverageFeePerUserSession(BaseView):
    """
    GET params same as PostsFeeCurator
    """

    title = 'Average fee per user session'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_fee_users',
            modifiers=SumModifier,
            api_query=self.request.GET,
            data_x='day',
            data_y='fee'
        )


class AverageFeePerAuthor(BaseView):
    """
    GET params same as PostsFeeCurator
    """
    title = 'Average fee per author'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_fee_author',
            modifiers=SumModifier,
            api_query=self.request.GET,
            data_x='day',
            data_y='fee'
        )


class PostsRatioDaily(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """
    title = 'Daily ratio'
    subtitle = 'Ratio of logged users and posts created by them'

    def get_data(self):
        return self.fetch_data(
            name_url='posts_ratio_daily',
            modifiers=AverageModifier,
            api_query=self.request.GET,
            data_x='date',
            data_y='ratio'
        )


class PostsRatioMonthly(BaseView):
    title = 'Monthly ratio'
    subtitle = 'Ratio of logged users and posts created by them'

    def get_data(self):
        return self.fetch_data(
            name_url='posts_ratio_monthly',
            modifiers=AverageModifier,
            data_x='date_to',
            data_y='ratio'
        )


class PostsSharing(BaseView):
    """
    GET param:
        date_to (default - yesterday)
        date_from (default - month ago)
        social_network (default - all)
    """

    name_url = 'posts_sharing'

    title = 'Posts sharings'
    subtitle = 'Amount of posts sharings per day'

    def get_data(self):
        return self.fetch_data(
            name_url=self.name_url,
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='day',
            data_y='count'
        )


class CommentsCount(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """

    title = 'Comments count'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='count_comments_weekly',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='day',
            data_y='count_comments'
        )


class CommentsPercentage(BaseView):
    """
    This endpoint shows percent of comments
    created through Steepshot relatively to all comments
    """

    title = 'Comments percent'
    subtitle = 'Comments through Steepshot / all comments'

    def get_data(self):
        return self.fetch_data(
            name_url='comments_percentage',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='day',
            data_y='percent'
        )


class VotesCountDaily(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
    """
    title = 'Votes count (daily)'
    subtitle = ''

    def get_data(self):

        api_params = get_date_range_from_request(self.request, day_difference=1)
        api_params['user_agent'] = self.request.GET.get('user_agent', None)

        return self.fetch_data(
            name_url='count_votes_weekly',
            api_query=api_params,
            modifiers=SumModifier,
            data_x='day',
            data_y='count_votes'
        )


class VotesCountMonthly(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
    """
    title = 'Votes count (monthly)'
    subtitle = ''

    def get_data(self):

        api_params = get_date_range_from_request(self.request, day_difference=30)
        api_params['user_agent'] = self.request.GET.get('user_agent', None)

        return self.fetch_data(
            name_url='count_votes_weekly',
            api_query=api_params,
            modifiers=SumModifier,
            data_x='day',
            data_y='count_votes'
        )


class AverageVotes(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """
    title = 'Average votes'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='votes_average_weekly',
            modifiers=AverageModifier,
            api_query=self.request.GET,
            data_x='day',
            data_y='votes_count'
        )


class GetHotTopNewCount(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
        date_from = default 7 days ago
    """
    title = 'Count of requests for top, hot, new'
    name_urls = ['count_hot', 'count_top', 'count_new']

    headers = [
        {'Date': 'string'},
        {'Steem hot': 'number'}, {'Golos hot': 'number'},
        {'Steem top': 'number'}, {'Golos top': 'number'},
        {'Steem new': 'number'}, {'Golos new': 'number'}
    ]

    def get_data(self):
        data = []
        for i in self.name_urls:
            res = self.fetch_data(
                name_url=i,
                api_query=self.request.GET,
                data_x='day',
                data_y='count_requests'
            )
            data.append(res['data'])
        group_data = lambda x: [x[0][0], x[0][1], x[0][2],
                                x[1][1], x[1][2],
                                x[2][1], x[2][2]]
        res_group = zip(data[0], data[1], data[2])
        res = []
        for i in res_group:
            res.append(group_data(i))
        return {'data': res, 'headers': self.headers}

    def get(self, request):
        data = self.get_data()
        return render(request, self.template_name, data)


class GetBrowseUsersCount(GetHotTopNewCount):
    title = 'Count users of requests for top, hot, new'
    name_urls = ['browse_users_count_hot', 'browse_users_count_top', 'browse_users_count_new']

    def get(self, request):
        data = self.get_data()
        return render(request, self.template_name, data)


class GetPostsCountNewUsers(BaseView):
    title = 'Posts count new users'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_count_new_users',
            modifiers=SumModifier,
            api_query=self.request.GET,
            data_x='day',
            data_y='count_post'
        )


class GetDAU(BaseView):
    title = 'DAU'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='DAU',
            modifiers=SumModifier,
            api_query=self.request.GET,
            data_x='day',
            data_y='active_users'
        )


class GetDAUNewUsers(BaseView):
    title = 'DAU new users'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='DAU_new_users',
            modifiers=SumModifier,
            api_query=self.request.GET,
            data_x='day',
            data_y='count_users'
        )


class GetUserPayout(BaseView):
    title = 'Users payout'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_payout_users',
            modifiers=SumModifier,
            api_query=self.request.GET,
            data_x='date',
            data_y='total_payout_per_day'
        )


class GetDailyTimeouts(BaseView):
    title = 'Timeouts daily'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='timeouts_daily',
            modifiers=SumModifier,
            api_query=self.request.GET,
            data_x='date',
            data_y='count'
        )


class GetLtvDaily(BaseView):
    title = 'LTV daily'
    subtitle = ''

    ltv_keys = ['beginning', 'three_month']

    headers = [
        {'Date': 'string'},
        {'LTV beginning': 'number'}, {'LTV three month': 'number'}
    ]

    def get_data(self):
        data = []
        for i in self.ltv_keys:
            res = self.fetch_data(
                    apis=ApiUrls.steem,
                    name_url='ltv_daily',
                    api_query=self.request.GET,
                    data_x='day',
                    data_y=i
            )
            data.append(res['data'])
        group_data = lambda x: [x[0][0], x[0][1], x[1][1]]
        res_group = zip(data[0], data[1])
        res = []
        for i in res_group:
            res.append(group_data(i))

        return {'data': res, 'headers': self.headers}


class CoolnessRequests(BaseView):
    '''
    This endpoint shows amount of requests
    to picture coolness endpoint
    '''

    title = 'Request to coolness endpoint'
    subtitle = 'Amount of requests per day'

    def get_data(self):
        return self.fetch_data(
            name_url='coolness_requests',
            api_query=self.request.GET,
            modifiers=SumModifier,
            data_x='day',
            data_y='count'
        )


class SteepshotVotes(BaseView):
    title = 'Steepshot votes'
    subtitle = 'Sum weight of votes per day divided on 100 (in percents)'

    def get_data(self):
        return self.fetch_data(
            apis=ApiUrls.steem,
            name_url='steepshot_votes',
            api_query=self.request.GET,
            data_x='date',
            data_y='total'
        )

class GetTotalActivePowerDaily(BaseView):
    title = 'Total Active Power'
    subtitle = 'Daily snapshot in %'

    def get_data(self):
        return self.fetch_data(
            apis=ApiUrls.steem,
            name_url='total_active_power_daily',
            api_query=self.request.GET,
            data_x='created_at',
            data_y='total_steem_power'
        )


class DeviceUsage(BaseView):
    title = 'Device usage'
    subtitle = 'Amount of post creations via device'

    name_url = 'device_usage'
    device_types = ['iOS', 'web', 'android']

    headers = [
        {'Date': 'string'},
        {'iOS': 'number'},
        {'Web': 'number'},
        {'Android': 'number'},
    ]

    def get_data(self):
        api_url = settings.REQUESTS_URL.get(self.name_url, '{url}').format(url=settings.STEEM_V1)

        fetched_data = []
        response = requests.get(api_url)
        if response.status_code == 200:
            fetched_data = response.json()

        data = {'headers': self.headers, 'data': []}
        for i in fetched_data:
            items_list = [i['date']]
            for device in self.device_types:
                items_list.append(i['counts'].get(device, 0))

            data['data'].append(items_list)

        data['data'] = sorted(data['data'], key=lambda x: x[0])
        return data


class GetAllGraphsOnePage(BaseView):

    template_name = 'all_stats_one_page.html'
    names_stats_endpoints = {
        'active_users_monthly': {'title': 'MAU', 'data_x': 'date_to', 'data_y': 'active_users'},
        'user_sessions_daily': {'title': 'Count sessions', 'data_x': 'day', 'data_y': 'count_sessions'},
        'new_users_daily': {'title': 'Count new users daily', 'data_x': 'day', 'data_y': 'count_users'},
        'new_users_monthly': {'title': 'Count new  users monthly', 'data_x': 'date_to', 'data_y': 'count_new_users'},
        'new_users_percent_daily': {'title': 'New users percent daily', 'data_x': 'day', 'data_y': 'percent'},
        'DAU': {'title': 'DAU', 'data_x': 'day', 'data_y': 'active_users'},
        'DAU_new_users': {'title': 'DAU new users', 'data_x': 'day', 'data_y': 'count_users'},
        'posts_payout_users': {'title': 'Users payout', 'data_x': 'date', 'data_y': 'total_payout_per_day'},
        'posts_count_daily': {'title': 'Count posts daily', 'data_x': 'day', 'data_y': 'count_posts'},
        'posts_count_new_users': {'title': 'Count posts daily from new users', 'data_x': 'day', 'data_y': 'count_posts'},
        'posts_fee_daily': {'title': 'Benefeciaries payout', 'data_x': 'date', 'data_y': 'total_payout_per_day'},
        'count_hot': {'title': 'Count of requests for hot', 'data_x': 'day', 'data_y': 'count_requests'},
        'count_top': {'title': 'Count of requests for top', 'data_x': 'day', 'data_y': 'count_requests'},
        'count_new': {'title': 'Count of requests for new', 'data_x': 'day', 'data_y': 'count_requests'},
        'browse_users_count_new': {'title': 'Count users of requests for new', 'data_x': 'day', 'data_y': 'count_requests'},
        'browse_users_count_hot': {'title': 'Count users of requests for hot', 'data_x': 'day', 'data_y': 'count_requests'},
        'browse_users_count_top': {'title': 'Count users of requests for top', 'data_x': 'day', 'data_y': 'count_requests'},
        'count_comments_weekly': {'title': 'Comments count', 'data_x': 'day', 'data_y': 'count_comments'},
        'count_votes_weekly': {'title': 'Votes count for new', 'data_x': 'day', 'data_y': 'count_votes'},
        'timeouts_daily': {'title': 'Timeouts daily', 'data_x': 'date', 'data_y': 'count'},
        'total_active_power_daily': {'title': 'Total Active Power', 'data_x': 'created_at', 'data_y': 'total_steem_power'},
    }

    def get_data(self, name_graph):
        api_url = settings.REQUESTS_URL.get(name_graph, '{url}').format(url=settings.STEEM_V1)
        res = {
            'data': [],
            'data_x': self.names_stats_endpoints[name_graph]['data_x'],
            'data_y': self.names_stats_endpoints[name_graph]['data_y'],
            'title': self.names_stats_endpoints[name_graph]['title'],
            'chart_div': name_graph,
        }
        months = 3
        days = 30
        date_to = date.today()
        date_from = date_to - timedelta(days=days * months)
        api_query = {
            'date_from': date_from,
            'date_to': date_to
        }
        response = requests.get(api_url, params=api_query)
        if response.status_code == 200:
            fetched_data = response.json()
            if 'result' in fetched_data:
                fetched_data = fetched_data['result']
            fetched_data = sorted(fetched_data, key=lambda x: x[res['data_x']])
            res['data'] = fetched_data
            print(len(res['data']))
        return res

    def get(self, request):
        if request.GET.get('graph'):
            name_graph = request.GET.get('graph')
            data = self.get_data(name_graph)
            return JsonResponse(data, safe=False)
        else:
            return render(request, self.template_name, {})
