import datetime
import requests
import logging
from django.conf import settings
from django.http import JsonResponse

from requests.exceptions import HTTPError, ConnectionError
from json.decoder import JSONDecodeError

from django.shortcuts import render
from dpix_io.graph.views import BaseView
from dpix_io.table_stats.helpers import str_from_datetime

logger = logging.getLogger(__name__)


class GetDashboard(BaseView):
    template_name = 'dashboard.html'

    graph_1 = {'name_graph': 'DAU and DAU new users',
                 'name_data_line_1': 'DAU',
                 'name_data_line_2': 'DAU new users',
                 'name_div': 'graph1',
                 'urls': [
                    {'url': 'DAU'},
                    {'url': 'DAU_new_users'}
                ]}
    graph_2 = {'name_graph': 'Count posts and count post from new users',
                 'name_data_line_1': 'Count posts',
                 'name_data_line_2': 'Count post new users',
                 'name_div': 'graph2',
                 'urls': [
                    {'url': 'posts_count_daily'},
                    {'url': 'posts_count_new_users'}
                ]}
    graph_3 = {'name_graph': 'Count comments and count votes',
                 'name_data_line_1': 'Count comments',
                 'name_data_line_2': 'Count votes',
                 'name_div': 'graph3',
                 'urls': [
                    {'url': 'count_comments_weekly'},
                    {'url': 'count_votes_weekly'}
                ]}
    graph_4 = {'name_graph': 'Count payouts (BEX * today\'s USD rate)',
                 'name_data_line_1': 'fee users',
                 'name_data_line_2': 'fee dPix',

               'name_div': 'graph4',
                 'urls': [
                    {'url': 'posts_payout_users'},
                    {'url': 'posts_fee_daily'},
                ]}

    graph_5 = {'name_graph': 'Count payouts (in BEX)',
                 'name_data_line_1': 'fee users',
                 'name_data_line_2': 'fee dPix',

               'name_div': 'graph5',
                 'urls': [
                    {'url': 'posts_payout_users'},
                    {'url': 'posts_fee_daily'},
                ]}

    graph_6 = {'name_graph': 'Timeouts daily',
                 'name_data_line_1': 'timeouts daily',

               'name_div': 'graph6',
                 'urls': [
                    {'url': 'timeouts_daily'},
                ]}

    graph_7 = {'name_graph': 'LTV daily (USD)',
               'name_data_line_1': 'LTV beginning',
               'name_data_line_2': 'LTV 3 months',
               'name_div': 'graph7',
               'list_keys_ltv': ['beginning', 'three_month'],
               'urls': [
                    {'url': 'ltv_daily'}
                ]}

    graph_8 = {'name_graph': 'LTV daily (BEX)',
               'name_data_line_1': 'LTV beginning',
               'name_data_line_2': 'LTV 3 months',
               'name_div': 'graph8',
               'list_keys_ltv': ['beginning', 'three_month'],
               'urls': [
                    {'url': 'ltv_daily'}
                ]}

    graph_9 = {'name_graph': 'Total Active Power daily (%)',
               'name_data_line_1': 'TAP daily',
               'name_div': 'graph9',
               'urls': [
                    {'url': 'total_active_power_daily'}
                ]}

    def get_data_x_and_data_y(self, request_dict):
        if 'ltv' in request_dict:
            data_y = 'ltv'
            data_x = 'day'
        else:
            for k, v in request_dict.items():
                if isinstance(v, str):
                    data_x = k
                    continue
                data_y = k

        return data_x, data_y

    def _sort_data_from_request(self, data, last_iter=False):
        try:
            data_x, data_y = self.get_data_x_and_data_y(data[0])
        except IndexError:
            return []

        sort_date = lambda x: x[data_x]

        if last_iter:
            return [i[data_x] for i in sorted(data, key=sort_date)]
        else:
            return [i[data_y] for i in sorted(data, key=sort_date)]

    def _make_api_query(self, date_to, date_from):
        return {'date_to': date_to, 'date_from': date_from}

    def _get_data_graph(self, graph_num, api_query=None):
        if graph_num == '1':
            graph = self.graph_1
        elif graph_num == '2':
            graph = self.graph_2
        elif graph_num == '3':
            graph = self.graph_3
        elif graph_num == '4':
            graph = self.graph_4
        elif graph_num == '5':
            api_query['currency'] = 'bex'
            graph = self.graph_5
        elif graph_num == '6':
            graph = self.graph_6
        elif graph_num == '7':
            graph = self.graph_7
        elif graph_num == '8':
            graph = self.graph_8
            api_query['currency'] = 'bex'
        else:
            graph = self.graph_9
        print(api_query, 'API!')
        try:
            name_data_line_2 = graph['name_data_line_2']
        except KeyError:
            name_data_line_2 = ''
        res_graph = {
                'title': graph['name_graph'],
                'name_div': graph['name_div'],
                'name_data_line_1': graph['name_data_line_1'],
                'name_data_line_2': name_data_line_2,
                'data_dpay': [],
                'data_dweb': [],
                'data_sum': [],
            }
        count_iter = len(graph['urls'])
        for count, i in enumerate(graph['urls'], start=1):
            try:
                data_dpay = requests.get(settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.DPAY_V1), params=api_query).json()
                if graph_num != '7' and graph_num != '8':
                    data_dweb = requests.get(settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.GOLOS_V1), params=api_query).json()
                else:
                    data_dweb = {}
                if 'result' in data_dpay:
                    data_dpay = data_dpay['result']
                if 'result' in data_dweb:
                    data_dweb = data_dweb['result']
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
                list_date = self._sort_data_from_request(data_dpay, last_iter=True)
                res_graph['date'] = list_date

            if graph_num == '7' or graph_num == '8':
                data_dpay = self._sort_data_from_request(data_dpay)
                for key in graph['list_keys_ltv']:
                    res_graph['data_dpay'].append([d[key] for d in data_dpay])
            else:
                data_dpay = self._sort_data_from_request(data_dpay)
                res_graph['data_dpay'].append(data_dpay)
                data_dweb = self._sort_data_from_request(data_dweb)
                data_sum = list(map(lambda x: x[0] + x[1], zip(data_dpay, data_dweb)))
                res_graph['data_dweb'].append(data_dweb)
                res_graph['data_sum'].append(data_sum)
        return res_graph

    def get(self, request):
        date_to = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=1))
        date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=8))
        if request.GET.get('graph'):
            graph_num = request.GET.get('graph')
            if request.GET.get('date_from') or request.GET.get('date_to'):
                date_to = request.GET.get('date_to', date_to)
                date_from = request.GET.get('date_from', date_from)
            api_query = self._make_api_query(date_to, date_from)
            data = self._get_data_graph(graph_num, api_query=api_query)
            return JsonResponse(data)
        else:
            return render(request, self.template_name)
