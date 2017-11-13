import datetime
import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from steepshot_io.graph.views import BaseView
from steepshot_io.table_stats.helpers import str_from_datetime
from steepshot_io.graph.data_modifiers import SumModifier

graph_1 = ['DAY', 'DAY_new_users']
graph_2 = ['posts_count_daily', 'posts_count_new_users']
graph_3 = ['count_comments_weekly', 'count_votes_weekly']
# graph_4 = []


class GetDashboard(BaseView):
    template_name = 'dashboard.html'
    date_to = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=1))
    date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=7))
    api_query = {'date_to': date_to, 'date_from': date_from}
    all_graphs = [
        {'name_graph': 'DAY and DAY new users',
         'urls': [
                    {'url': 'DAY', 'data_x': 'day', 'data_y': 'active_users', 'name_data': 'DAY'},
                    {'url': 'DAY_new_users', 'data_x': 'day', 'data_y': 'count_users', 'name_data': 'DAY new users'}
                ]},
        {'name_graph': 'Count posts and count post from new users',
         'urls': [
                    {'url': 'posts_count_daily', 'data_x': 'day', 'data_y': 'count_posts', 'name_data': 'Count posts'},
                    {'url': 'posts_count_new_users', 'data_x': 'day', 'data_y': 'count_post', 'name_data': 'Count post new users'}
                ]},
        {'name_graph': 'Count comments and count votes',
         'urls': [
                    {'url': 'count_comments_weekly', 'data_x': 'day', 'data_y': 'count_comments', 'name_data': 'Count comments'},
                    {'url': 'count_votes_weekly', 'data_x': 'day', 'data_y': 'count_votes', 'name_data': 'Count votes',}
                ]}
                 ]

    def get_data(self):
        res_all_graphs = []
        for i in self.all_graphs:
            res_graph_one = []
            for j in i['urls']:
                data_x = j['data_x']
                data_y = j['data_y']
                name_url = j['url']
                data = self.fetch_data(
                        name_url=name_url,
                        data_x=data_x,
                        data_y=data_y,
                        modifiers=SumModifier,
                        api_query=self.api_query
                )
                data.update({'name_line': j['name_data']})
                res_graph_one.append(data)
            dict_res = {'title': i['name_graph'], 'data': [res_graph_one], }
            res_all_graphs.append(dict_res)
        return res_all_graphs

    def _group_data(self, list_request_data):
        res = []
        for i in list_request_data:
            for j, k in i['data']:
                res_zip = zip(j['data'], k['data'])
                headers = [{'Date': 'string'}, {j['name_line']: 'number'}, {k['name_line']: 'number'}]
                data = {'title': i['title'], 'headers': headers, 'data_steem': [], 'data_golos': [], 'data_sum': []}
                for x, y in res_zip:
                    data_steem = [x[0], x[1], y[1]]
                    data_golos = [x[0], x[2], y[2]]
                    data_sum = [x[0], x[3], y[3]]
                    data['data_steem'].append(data_steem)
                    data['data_golos'].append(data_golos)
                    data['data_sum'].append(data_sum)
                res.append(data)
        return res

    def get(self, request):
        data = self.get_data()
        graphs = self._group_data(data)
        # data = self.fetch_data(
        #     name_url='DAY',
        #     data_x='day',
        #     data_y='active_users'
        # )
        # data.update({
        #     'title': self.title,
        #     'subtitle': self.subtitle
        # })
        # print(data)

        return render(request, self.template_name, {'data': graphs})
