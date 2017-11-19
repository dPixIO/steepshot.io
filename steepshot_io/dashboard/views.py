import datetime
import requests
import logging
from django.conf import settings
from django.http import JsonResponse

from requests.exceptions import HTTPError, ConnectionError
from json.decoder import JSONDecodeError

from django.shortcuts import render
from steepshot_io.graph.views import BaseView
from steepshot_io.table_stats.helpers import str_from_datetime

logger = logging.getLogger(__name__)


class GetDashboard(BaseView):
    template_name = 'test2.html'
    date_to = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=1))
    date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=4))
    graph_1 = {'name_graph': 'DAY and DAY new users',
                 'name_data_line_1': 'DAU',
                 'name_data_line_2': 'DAU new users',
                 'name_div': 'graph1',
                 'urls': [
                    {'url': 'DAY', 'data_x': 'day', 'data_y': 'active_users'},
                    {'url': 'DAY_new_users', 'data_x': 'day', 'data_y': 'count_users'}
                ]}
    graph_2 = {'name_graph': 'Count posts and count post from new users',
                 'name_data_line_1': 'Count posts',
                 'name_data_line_2': 'Count post new users',
                 'name_div': 'graph2',
                 'urls': [
                    {'url': 'posts_count_daily', 'data_x': 'day', 'data_y': 'count_posts'},
                    {'url': 'posts_count_new_users', 'data_x': 'day', 'data_y': 'count_post'}
                ]}
    graph_3 = {'name_graph': 'Count comments and count votes',
                 'name_data_line_1': 'Count comments',
                 'name_data_line_2': 'Count votes',
                 'name_div': 'graph3',
                 'urls': [
                    {'url': 'count_comments_weekly', 'data_x': 'day', 'data_y': 'count_comments'},
                    {'url': 'count_votes_weekly', 'data_x': 'day', 'data_y': 'count_votes'}
                ]}

    def _get_data_graph(self, graph_num, api_query=None):
        if not api_query:
            api_query = self._make_api_query(self.date_to, self.date_from)

        if graph_num == '1':
            graph = self.graph_1
        elif graph_num == '2':
            graph = self.graph_2
        else:
            graph = self.graph_3

        res_graph = {
                'title': graph['name_graph'],
                'name_div': graph['name_div'],
                'name_data_line_1': graph['name_data_line_1'],
                'name_data_line_2': graph['name_data_line_2'],
                'data_steem': [],
                'data_glos': [],
                'data_sum': [],
            }
        count_iter = len(graph['urls'])
        for count, i in enumerate(graph['urls'], start=1):
            try:
                data_steem = requests.get(settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.STEEM_V1), params=api_query).json()
                data_golos = requests.get(settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.GOLOS_V1), params=api_query).json()
            except JSONDecodeError as e:
                logger.error('Failed to parse json: {err}.'.format(err=e))
                continue
            except (ConnectionError, HTTPError) as e:
                logger.error('Failed to connect to {platform} server: {err}.'.format(platform=i.value, err=e))
                continue
            except Exception as e:
                logger.error('Unexpected error: {err}'.format(err=e))
                continue

            if count == count_iter:
                list_date = self._sort_data_from_request(data_steem, i['data_x'], i['data_y'], last_iter=True)
                res_graph['date'] = list_date
            data_steem = self._sort_data_from_request(data_steem, i['data_x'], i['data_y'])
            data_golos = self._sort_data_from_request(data_golos, i['data_x'], i['data_y'])
            data_sum = list(map(lambda x: x[0] + x[1], zip(data_steem, data_golos)))
            res_graph['data_steem'].append(data_steem)
            res_graph['data_glos'].append(data_golos)
            res_graph['data_sum'].append(data_sum)
        return res_graph

    def get(self, request):
        if request.GET.get('graph'):
            graph_num = request.GET.get('graph')
            if request.GET.get('date_from'):
                date_from = request.GET.get('date_from')
                date_to = request.GET.get('date_to')
                api_query = self._make_api_query(date_to, date_from)
                data = self._get_data_graph(graph_num=graph_num, api_query=api_query)
                return JsonResponse(data)
            data = self._get_data_graph(graph_num=graph_num)
            return JsonResponse(data)
        return render(request, self.template_name)

    def _sort_data_from_request(self, data, date_x, date_y, last_iter=False):
        sort_date = lambda x: x[date_x]
        if last_iter:
            return [i[date_x] for i in sorted(data, key=sort_date)]
        else:
            return [i[date_y] for i in sorted(data, key=sort_date)]

    # def get(self, request):
    #     res = []
    #     api_query = self._make_api_query(self.date_to, self.date_from)
    #     for graph in self.all_graphs:
    #         res_graph = {
    #             'title': graph['name_graph'],
    #             'name_div': graph['name_div'],
    #             'name_data_line_1': graph['name_data_line_1'],
    #             'name_data_line_2': graph['name_data_line_2'],
    #             'data_steem': [],
    #             'data_glos': [],
    #             'data_sum': [],
    #         }
    #         count_iter = len(graph['urls'])
    #         for j, k in enumerate(graph['urls'], start=1):
    #             data_steem = requests.get(settings.REQUESTS_URL.get(k['url'], '{url}').format(url=settings.STEEM_V1), params=api_query).json()
    #             data_golos = requests.get(settings.REQUESTS_URL.get(k['url'], '{url}').format(url=settings.GOLOS_V1), params=api_query).json()
    #             if j == count_iter:
    #                 list_date = self._sort_data_from_request(data_steem, k['data_x'], k['data_y'], last_iter=True)
    #                 res_graph['date'] = list_date
    #             data_steem = self._sort_data_from_request(data_steem, k['data_x'], k['data_y'])
    #             data_golos = self._sort_data_from_request(data_golos, k['data_x'], k['data_y'])
    #             data_sum = list(map(lambda x: x[0] + x[1], zip(data_steem, data_golos)))
    #             res_graph['data_steem'].append(data_steem)
    #             res_graph['data_glos'].append(data_golos)
    #             res_graph['data_sum'].append(data_sum)
    #         res.append(res_graph)
    #     return render(request, self.template_name, {'res': res})
    #
    def _make_api_query(self, date_to, date_from):
        return {'date_to': date_to, 'date_from': date_from}

    # def post(self, request):
    #     if request.POST.get('date_to') or request.POST.get('date_from'):
    #         date_to = request.POST.get('date_to') if request.POST.get('date_to') else self.date_to
    #         date_from = request.POST.get('date_from') if request.POST.get('date_from') else self.date_from
    #         api_query = self._make_api_query(date_to, date_from)
    #         data = self._get_data_graph()
        #     if request.POST.get('date-choice'):
    #         date_api = request.POST.get('date-choice')
    #         if date_api == '6':
    #             days = 30
    #             months = 6
    #             date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=days * months))
    #             api_query = self._make_api_query(self.date_to, date_from)
    #         elif date_api == '30':
    #             date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=30))
    #             api_query = self._make_api_query(self.date_to, date_from)
    #         else:
    #             api_query = self._make_api_query(self.date_to, self.date_from)
    #     elif request.POST.get('date_to') or request.POST.get('date_from'):
    #         date_to = request.POST.get('date_to') if request.POST.get('date_to') else self.date_to
    #         date_from = request.POST.get('date_from') if request.POST.get('date_from') else self.date_from
    #         api_query = self._make_api_query(date_to, date_from)
    #     platform = request.POST.get('platform')
    #     data = self.get_data(api_query=api_query)
    #     data_graphs = self._group_data(data)
    #     return render(request, self.template_name, {'data': data_graphs, 'platform': platform})

