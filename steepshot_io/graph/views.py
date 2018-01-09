import logging
from enum import Enum
from json.decoder import JSONDecodeError
from typing import Dict

import requests
from django.conf import settings
from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from requests.exceptions import HTTPError, ConnectionError

from steepshot_io.graph.data_modifiers import SumModifier, AverageModifier, BaseModifier
from steepshot_io.graph.utils import get_date_range_from_request


logger = logging.getLogger(__name__)


class ApiUrls(Enum):
    steem = 'steem'
    golos = 'golos'


class BaseView(View):
    template_name = 'graph.html'
    title = ''
    subtitle = ''

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
    """

    title = 'Monthly active users'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='active_users_monthly',
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
            api_query=self.request.GET,
            modifiers=SumModifier,
            name_url='posts_fee_daily',
            data_x='date',
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


class VotesCountDaily(BaseView):
    """
    GET param:
        date_to = default date (yesterday)
    """
    title = 'Votes count (daily)'
    subtitle = ''

    def get_data(self):

        api_params = get_date_range_from_request(self.request, day_difference=1)
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


class GetAllStats(BaseView):

    template_name = 'all_stats.html'

    names_stats_endpoints = [
        {'active_users_monthly': 'MAU'},
        {'user_sessions_daily': 'Count sessions'},
        {'new_users_daily': 'Count new users daily'},
        {'new_users_monthly': 'Count new users monthly'},
        {'new_users_percent_daily': 'Percent new users'},
        {'DAU': 'DAU'},
        {'DAU_new_users': 'DAU new users'},
        {'posts_average_per_author': 'Average posts per author'},
        {'posts_payout_users': 'Users payout'},
        {'count_posts_daily': 'Count posts'},
        {'posts_count_new_users': 'Count post from new users'},
        {'count_posts': 'Count posts monthly'},
        {'posts_fee_daily': 'Benefeciary payout'},
        {'posts_fee_weekly': 'Posts fee weekly'},
        {'posts_fee_author': 'Average fee author per day'},
        {'posts_fee_users': 'Average fee user per day'},
        {'ratio_daily': 'Daily ratio (Ratio of logged users and posts created by them)'},
        {'ratio_monthly': 'Monthly ratio'},
        {'count_requests': 'Count of requests for top, new, hot'},
        {'browse_users_request': 'Count users of requests for new, top, hot'},
        {'count_comments_weekly': 'Count comments'},
        {'count_votes_daily': 'Count votes daily'},
        {'count_votes_monthly': 'Count votes monthly'},
        {'votes_average_weekly': 'Average votes user per day'}
    ]

    def get(self, request):
        all_url = self.names_stats_endpoints
        return render(request, self.template_name, {'data': all_url})

    def post(self, request):
        name_url = request.POST['name_url']
        return redirect('graph:{}'.format(name_url))