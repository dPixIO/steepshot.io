import datetime
import requests
import logging
from django.conf import settings

from requests.exceptions import HTTPError, ConnectionError
from json.decoder import JSONDecodeError

from django.shortcuts import render
from steepshot_io.graph.views import BaseView
from steepshot_io.table_stats.helpers import str_from_datetime
from steepshot_io.graph.data_modifiers import SumModifier

logger = logging.getLogger(__name__)


class GetDashboard(BaseView):
    pass
#     template_name = 'test.html'
#     date_to = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=1))
#     date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=7))
#     all_graphs = [
#         {'name_graph': 'DAY and DAY new users',
#          'urls': [
#                     {'url': 'DAY', 'data_x': 'day', 'data_y': 'active_users', 'name_data': 'DAY'},
#                     {'url': 'DAY_new_users', 'data_x': 'day', 'data_y': 'count_users', 'name_data': 'DAY new users'}
#                 ]},
#         {'name_graph': 'Count posts and count post from new users',
#          'urls': [
#                     {'url': 'posts_count_daily', 'data_x': 'day', 'data_y': 'count_posts', 'name_data': 'Count posts'},
#                     {'url': 'posts_count_new_users', 'data_x': 'day', 'data_y': 'count_post', 'name_data': 'Count post new users'}
#                 ]},
#         {'name_graph': 'Count comments and count votes',
#          'urls': [
#                     {'url': 'count_comments_weekly', 'data_x': 'day', 'data_y': 'count_comments', 'name_data': 'Count comments'},
#                     {'url': 'count_votes_weekly', 'data_x': 'day', 'data_y': 'count_votes', 'name_data': 'Count votes',}
#                 ]}
#                  ]
#
#     def _get_data(self, api_query=None):
#         if not api_query:
#             api_query = self._make_api_query(self.date_to, self.date_from)
#
#         for i in self.all_graphs:
#             for j in i['urls']:
#                 aaa = settings.REQUESTS_URL.get(j, '{url}').format(url=settings.STEEM_V1)
#                 print(aaa)
#                 import pdb
#                 pdb.set_trace()
#                 data = requests.get(settings.REQUESTS_URL.get(j, '{url}').format(url=settings.STEEM_V1))
#             # try:
            #     data = requests.get(all_endpoint_urls.get(api), params=api_query).json()
            #     if 'result' in data:
            #         data = data['result']
            # except JSONDecodeError as e:
            #     logger.error('Failed to parse json: {err}.'.format(err=e))
            #     continue
            # except (ConnectionError, HTTPError) as e:
            #     logger.error('Failed to connect to {platform} server: {err}.'.format(platform=api.value, err=e))
            #     continue
            # except Exception as e:
            #     logger.error('Unexpected error: {err}'.format(err=e))
            #     continue


    #
    # def get(self, request):
    #     res = []
    #     api_query = self._make_api_query(self.date_to, self.date_from)
    #     for i in self.all_graphs:
    #         res_graph = []
    #         for j in i['urls']:
    #             data_steem = requests.get(settings.REQUESTS_URL.get(j['url'], '{url}').format(url=settings.STEEM_V1), params=api_query).json()
    #             data_golos = requests.get(settings.REQUESTS_URL.get(j['url'], '{url}').format(url=settings.GOLOS_V1), params=api_query).json()
    #             res_graph.append(data_steem)
    #             res_graph.append(data_golos)
    #         res.append(res_graph)
    #     print(res)
    #     import pdb
    #     pdb.set_trace()
    #     return render(request, self.template_name, {'urls': self.all_graphs})

# def get_data(self, api_query=None):
    #     if not api_query:
    #         api_query = self._make_api_query(self.date_to, self.date_from)
    #     res_all_graphs = []
    #     for i in self.all_graphs:
    #         res_graph_one = []
    #         for j in i['urls']:
    #             data_x = j['data_x']
    #             data_y = j['data_y']
    #             name_url = j['url']
    #             data = self.fetch_data(
    #                     name_url=name_url,
    #                     data_x=data_x,
    #                     data_y=data_y,
    #                     modifiers=SumModifier,
    #                     api_query=api_query
    #             )
    #             data.update({'name_line': j['name_data']})
    #             res_graph_one.append(data)
    #         dict_res = {'title': i['name_graph'], 'data': [res_graph_one], }
    #         res_all_graphs.append(dict_res)
    #     return res_all_graphs
    #
    # def _group_data(self, list_request_data):
    #     res = []
    #     for i in list_request_data:
    #         for j, k in i['data']:
    #             res_zip = zip(j['data'], k['data'])
    #             headers = [{'Date': 'string'}, {j['name_line']: 'number'}, {k['name_line']: 'number'}]
    #             data = {'title': i['title'], 'headers': headers, 'data_steem': [], 'data_golos': [], 'data_sum': []}
    #             for x, y in res_zip:
    #                 data_steem = [x[0], x[1], y[1]]
    #                 data_golos = [x[0], x[2], y[2]]
    #                 data_sum = [x[0], x[3], y[3]]
    #                 data['data_steem'].append(data_steem)
    #                 data['data_golos'].append(data_golos)
    #                 data['data_sum'].append(data_sum)
    #             res.append(data)
    #     return res
    #
    # def _make_api_query(self, date_to, date_from):
    #     return {'date_to': date_to, 'date_from': date_from}
    #
    # def get(self, request):
    #     data = self.get_data()
    #     data_graphs = self._group_data(data)
    #     import json
    #     asd = json.dumps({'asd':'asdf'})
    #     platform = 'steem'
    #     return render(request, self.template_name, {'data': data_graphs, 'platform': platform, 'asd':asd})
    #
    # def post(self, request):
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

