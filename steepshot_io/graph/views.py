import logging
from enum import Enum
from json.decoder import JSONDecodeError
from typing import Dict

import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from requests.exceptions import HTTPError, ConnectionError

from steepshot_io.graph.data_modifiers import SumModifier, AverageModifier, BaseModifier

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

        if len(apis) > 1 and modifiers:
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


class GetPostFee(BaseView):
    title = 'Posts payment'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            apis=ApiUrls.steem,
            api_query=self.request.GET,
            name_url='post_fee',
            data_x='day',
            data_y='count_fee'
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


class PostsCountWeekly(BaseView):
    title = 'Posts count weekly'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='count_posts_weekly',
            modifiers=SumModifier,
            data_x='day',
            data_y='count_post'
        )


class PostsCountDaily(BaseView):
    title = 'Posts count daily'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            apis=ApiUrls.steem,
            name_url='posts_count_daily',
            data_x='day',
            data_y='count_posts'
        )


class UsersActive(BaseView):
    title = 'Monthly active users'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='active_users',
            modifiers=SumModifier,
            data_x='date_to',
            data_y='active_users'
        )


class PostsRatioDaily(BaseView):
    title = 'Daily ratio'
    subtitle = 'Ratio of logged users and posts created by them'

    def get_data(self):
        return self.fetch_data(
            name_url='ratio_daily',
            modifiers=AverageModifier,
            data_x='date',
            data_y='ratio'
        )


class PostsRatioMonthly(BaseView):
    title = 'Monthly ratio'
    subtitle = 'Ratio of logged users and posts created by them'

    def get_data(self):
        return self.fetch_data(
            name_url='ratio_monthly',
            modifiers=AverageModifier,
            data_x='date_to',
            data_y='ratio'
        )


class UsersNewCountDaily(BaseView):
    title = 'New users count'
    subtitle = 'Daily count of new users'

    def get_data(self):
        return self.fetch_data(
            name_url='new_users',
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
            name_url='users_percent_daily',
            modifiers=AverageModifier,
            data_x='day',
            data_y='percent'
        )


class PostsAverageWeekly(BaseView):
    title = 'Post average (weekly)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_average_weekly',
            modifiers=AverageModifier,
            data_x='day',
            data_y='count_post'
        )


class PostsAverageAuthor(BaseView):
    title = 'Posts average per author'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_average_author',
            modifiers=AverageModifier,
            data_x='day',
            data_y='count_posts'
        )


class VotesCountWeekly(BaseView):
    title = 'Votes count (weekly)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='count_votes_weekly',
            modifiers=SumModifier,
            data_x='day',
            data_y='count_votes'
        )


class AverageVotesWeekly(BaseView):
    title = 'Average votes (weekly)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='votes_average_weekly',
            modifiers=AverageModifier,
            data_x='day',
            data_y='votes_count'
        )


class CommentsCountWeekly(BaseView):
    title = 'Comments count (weekly)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='count_comments_weekly',
            modifiers=SumModifier,
            data_x='day',
            data_y='count_comments'
        )


class CountUsersSessions(BaseView):
    title = 'User session count (weekly)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='users_count_session',
            modifiers=SumModifier,
            data_x='day',
            data_y='count_sessions'
        )


class PostsFeeWeekly(BaseView):
    title = 'Posts fee (weekly)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_fee_weekly',
            modifiers=SumModifier,
            data_x='day',
            data_y='fee'
        )


class PostsFeeUsers(BaseView):
    title = 'Posts fee (users)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_fee_users',
            modifiers=SumModifier,
            data_x='day',
            data_y='fee'
        )


class PostsFeeAuthor(BaseView):
    title = 'Posts fee (author)'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_fee_author',
            modifiers=SumModifier,
            data_x='day',
            data_y='fee'
        )
