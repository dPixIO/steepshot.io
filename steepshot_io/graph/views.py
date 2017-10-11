import logging
from collections import OrderedDict
from json.decoder import JSONDecodeError
from typing import Dict

import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from requests.exceptions import HTTPError, ConnectionError

logger = logging.getLogger(__name__)

_STEEM_API_NAME = 'steem'
_GOLOS_API_NAME = 'golos'


class BaseView(View):
    template_name = 'graph.html'
    title = ''
    subtitle = ''

    def fetch_data(self,
                   data_x=None,
                   data_y=None,
                   name_url=None,
                   amount=True,
                   average=True,
                   platform=None,
                   reverse=True,
                   return_dict=False) -> Dict:
        endpoint_urls = OrderedDict(
            steem=settings.REQUESTS_URL.get(name_url, '{url}').format(url=settings.STEEM_V1),
            golos=settings.REQUESTS_URL.get(name_url, '{url}').format(url=settings.GOLOS_V1)
        )

        res = {
            'headers': [
                {'Date': 'string'},
                {'Steem': 'number'},
                {'Golos': 'number'}
            ],
            'data': []
        }
        res_data_idx_map = {}

        for i, url in enumerate(endpoint_urls, start=1):
            try:
                data = requests.get(endpoint_urls[url]).json()
                if 'result' in data:
                    data = data['result']
            except JSONDecodeError as e:
                logger.error('Failed to parse json: {err}.'.format(err=e))
                continue
            except (ConnectionError, HTTPError) as e:
                logger.error('Failed to connect to {platform} server: {err}.'.format(platform=url.upper(), err=e))
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
                    res['data'].append([key, 0, 0])
                res['data'][res_data_idx][i] = d.get(data_y)

        res['data'] = sorted(res['data'], key=lambda x: x[0])

        if amount:
            res['headers'].append({'Sum': 'number'})
            for i, row in enumerate(res['data']):
                res['data'][i] += [sum(row[1:3])]

        if average:
            res['headers'].append({'Average': 'number'})
            for i, row in enumerate(res['data']):
                res['data'][i] += [sum(row[1:3]) / 2]

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


class GetPostFee(View):
    template_name = 'graph.html'

    def _get_data(self, currency='VESTS', name_key=None, name_url=None, use_fee=True):
        values = []
        try:
            if not use_fee:
                currency = ''
            cur_url = settings.REQUESTS_URL[name_url].format(url=settings.STEEM_V1)
            res = requests.get(cur_url + currency).json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['day'], i[name_key]])
        except JSONDecodeError as e:
            logger.error('Failed to parse json {}'.format(e))
        except (ConnectionError, HTTPError) as e:
            logger.error('Failed to connect to {}'.format(e))
        except Exception as e:
            logger.error(e)
        return values

    def get(self, request, *args, **kwargs):
        if 'currency' in request.GET:
            currency = request.GET['currency'].lower()
            values = self._get_data(currency=currency, name_key='count_fee', name_url='post_fee')
        else:
            values = self._get_data(name_key='count_fee', name_url='post_fee')
        name = 'fee in day'
        return render(request, self.template_name, {'values': values, 'name_1': name})


class GetPostsCountMonthly(BaseView):
    title = 'Posts count'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='posts_count_monthly',
            average=False,
            data_x='date_to',
            data_y='posts_count'
        )


class GetActiveUsers(BaseView):
    title = 'Monthly active users'
    subtitle = ''

    def get_data(self):
        return self.fetch_data(
            name_url='active_users',
            average=False,
            data_x='date_to',
            data_y='active_users'
        )


class GetCountPostDaily(GetPostFee):
    def get(self, request, *args, **kwargs):
        values = self._get_data(use_fee=False, name_url='posts_count_daily', name_key='count_posts')
        name = 'count posts'
        return render(request, self.template_name, {'values': values, 'name_1': name})


class GetRatioDaily(BaseView):
    title = 'Daily ratio'
    subtitle = 'Ratio of logged users and posts created by them'

    def get_data(self):
        return self.fetch_data(
            name_url='ratio_daily',
            amount=False,
            data_x='date',
            data_y='ratio'
        )

    # TODO: REMOVE THIS METHOD!
    def _group_steem_golos(self, list_steem, list_golos):
        res = []
        idx = 0
        while True:
            try:
                res.append([list_steem[idx][0], list_steem[idx][1], list_golos[idx][1]])
            except IndexError:
                break
            idx += 1
        return res


class GetRatioMonthly(BaseView):
    title = 'Monthly ratio'
    subtitle = 'Ratio of logged users and posts created by them'

    def get_data(self):
        return self.fetch_data(
            name_url='ratio_monthly',
            amount=False,
            data_x='date_to',
            data_y='ratio'
        )


class CountNewUsers(BaseView):
    title = 'New users count'
    subtitle = 'Daily count of new users'

    def get_data(self):
        return self.fetch_data(
            name_url='new_users',
            average=False,
            data_x='day',
            data_y='count_users'
        )


class CountNewUsersMonthly(BaseView):
    title = 'New users count'
    subtitle = 'Monthly count of new users'

    def get_data(self):
        return self.fetch_data(
            name_url='new_users_monthly',
            average=False,
            data_x='date_to',
            data_y='count_new_users'
        )


class CountPercentUsersDaily(CountNewUsers):
    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            name_1 = 'users percent daily ' + platform
            values = self.fetch_data(platform=platform, name_url='users_percent_daily',
                                     data_x='day', data_y='percent', reverse=False)[0]
            return render(request, self.template_name, {'values': values, 'name_1': name_1})
        else:
            values_steem, values_golos = self.fetch_data(name_url='users_percent_daily',
                                                         data_x='day', data_y='percent', reverse=False)
            values = self._group_steem_golos(values_steem, values_golos)
            flag_together = True
            name_1 = 'users percent daily steem'
            name_2 = 'users percent daily golos'
            return render(request, self.template_name, {'values': values, 'flag': flag_together,
                                                        'name_1': name_1, 'name_2': name_2})


class CountPostWeekly(CountNewUsers):
    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            name_1 = 'count posts ' + platform
            values = self.fetch_data(platform=platform, name_url='count_posts_weekly',
                                     data_x='day', data_y='count_post', reverse=False)[0]
            return render(request, self.template_name, {'values': values, 'name_1': name_1})
        else:
            values_steem, values_golos = self.fetch_data(name_url='count_posts_weekly',
                                                         data_x='day', data_y='count_post', reverse=False)
            values = self._group_steem_golos(values_steem, values_golos)
            flag_together = True
            name_1 = 'count posts steem'
            name_2 = 'count posts golos'
            return render(request, self.template_name, {'values': values, 'flag': flag_together,
                                                        'name_1': name_1, 'name_2': name_2})


# class PostsAverageWeekly(CountPostWeekly):
#     def get(self, request, *args, **kwargs):
#         if 'platform' in request.GET:
#             platform = request.GET['platform'].lower()
#             values = self._get_data(platform=platform, name_url='posts_average_weekly', data_x='day', data_y='count_post')[0]
#             name_1 = 'posts average ' + platform
#             return render(request, self.template_name, {'values': values, 'name_1': name_1})
#         else:
#             values_steem, values_golos = self._get_data(name_url='posts_average_weekly', data_x='day', data_y='count_post')
#             values = self._group_steem_golos(values_steem, values_golos)
#             flag_together = True
#             name_1 = 'posts average steem'
#             name_2 = 'posts average golos'
#             return render(request, self.template_name, {'values': values, 'flag': flag_together, 'name_1': name_1, 'name_2': name_2})


class PostsAverageAuthor(CountPostWeekly):
    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            name_1 = 'posts average ' + platform
            values = self.fetch_data(platform=platform, name_url='posts_average_author',
                                     data_x='day', data_y='count_posts', reverse=False)[0]
            return render(request, self.template_name, {'values': values, 'name_1': name_1})
        else:
            values_steem, values_golos = self.fetch_data(name_url='posts_average_author',
                                                         data_x='day', data_y='count_posts', reverse=False)
            values = self._group_steem_golos(values_steem, values_golos)
            flag_together = True
            name_1 = 'posts average steem'
            name_2 = 'posts average golos'
            return render(request, self.template_name, {'values': values, 'flag': flag_together,
                                                        'name_1': name_1, 'name_2': name_2})


class CountVotesWeekly(CountPostWeekly):
    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            name_1 = 'count votes ' + platform
            values = self.fetch_data(platform=platform, name_url='count_votes_weekly',
                                     data_x='day', data_y='count_votes', reverse=False)[0]
            return render(request, self.template_name, {'values': values, 'name_1': name_1})
        else:
            values_steem, values_golos = self.fetch_data(name_url='count_votes_weekly',
                                                         data_x='day', data_y='count_votes', reverse=False)
            values = self._group_steem_golos(values_steem, values_golos)
            flag_together = True
            name_1 = 'count votes steem'
            name_2 = 'count votes golos'
            return render(request, self.template_name,
                          {'values': values, 'flag': flag_together, 'name_1': name_1, 'name_2': name_2})


# class AverageVotesWeekly(CountVotesWeekly):
#     def get(self, request, *args, **kwargs):
#         if 'platform' in request.GET:
#             platform = request.GET['platform'].lower()
#             name_1 = 'average votes ' + platform
#             values = self._get_data(platform=platform, name_url='votes_average_weekly', data_x='day', data_y='votes_count', reverse=False)
#             return render(request, self.template_name, {'values': values, 'name_1': name_1})
#         else:
#             values_steem, values_golos = self._get_data(name_url='votes_average_weekly', data_x='day', data_y='votes_count', reverse=False)
#             values = self.group_steem_golos(values_steem, values_golos)
#             flag_together = True
#             name_1 = 'average votes steem'
#             name_2 = 'average votes golos'
#             return render(request, self.template_name,
#                           {'values': values, 'flag': flag_together, 'name_1': name_1, 'name_2': name_2})


class CountCommentsWeekly(CountPostWeekly):
    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            name_1 = 'count comments ' + platform
            values = self.fetch_data(platform=platform, name_url='count_comments_weekly',
                                     data_x='day', data_y='count_comments', reverse=False)[0]
            return render(request, self.template_name, {'values': values, 'name_1': name_1})
        else:
            values_steem, values_golos = self.fetch_data(name_url='count_comments_weekly',
                                                         data_x='day', data_y='count_comments', reverse=False)
            values = self._group_steem_golos(values_steem, values_golos)
            flag_together = True
            name_1 = 'count comments steem'
            name_2 = 'count comments golos'
            return render(request, self.template_name,
                          {'values': values, 'flag': flag_together, 'name_1': name_1, 'name_2': name_2})


# class CountUsersSessions(CountPostWeekly):
#     template_name = 'graph.html'
#
#     def get(self, request, *args, **kwargs):
#         if 'platform' in request.GET:
#             platform = request.GET['platform'].lower()
#             name_1 = 'count session ' + platform
#             values = self._get_data(platform=platform, name_url='users_count_session', data_x='day', data_y='count_sessions', reverse=False)
#             return render(request, self.template_name, {'values': values, 'name_1': name_1})
#         else:
#             values_steem, values_golos = self._get_data(name_url='users_count_session', data_x='day', data_y='count_sessions', reverse=False)
#             values = self._group_steem_golos(values_steem, values_golos)
#             flag_together = True
#             name_1 = 'count session steem'
#             name_2 = 'count session golos'
#             return render(request, self.template_name,
#                           {'values': values, 'flag': flag_together, 'name_1': name_1, 'name_2': name_2})


class PostsFeeWeekly(CountPostWeekly):
    def get(self, request, *args, **kwargs):
        current_url = request.resolver_match.url_name
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            name_1 = 'fee ' + platform
            values = self.fetch_data(platform=platform, name_url=current_url,
                                     data_x='day', data_y='fee', reverse=False)[0]
            return render(request, self.template_name, {'values': values, 'name_1': name_1})
        else:
            values_steem, values_golos = self.fetch_data(name_url=current_url,
                                                         data_x='day', data_y='fee', reverse=False)
            values = self._group_steem_golos(values_steem, values_golos)
            flag_together = True
            name_1 = 'fee steem'
            name_2 = 'fee golos'
            return render(request, self.template_name,
                          {'values': values, 'flag': flag_together, 'name_1': name_1, 'name_2': name_2})
