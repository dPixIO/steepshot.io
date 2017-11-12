import datetime
import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View
from steepshot_io.graph.views import BaseView
from steepshot_io.table_stats.helpers import str_from_datetime

graph_1 = ['DAY', 'DAY_new_users']
graph_2 = ['posts_count_daily', 'posts_count_new_users']
graph_3 = ['count_comments_weekly', 'count_votes_weekly']
# graph_4 = []


class GetDashboard(BaseView):
    template_name = 'dashboard.html'
    # title = 'AAAA'
    # subtitle = 'SSSSSSS'
    date_to = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=1))
    date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=7))
    api_query = {'date_to': date_to, 'date_from': date_from}
    all_graphs = [
        {'name': 'graph_1', 'urls': [{'url':'DAY','data_x':'day', 'data_y':'active_users'},
                                     {'url':'DAY_new_users', 'data_x':'day', 'data_y':'active_users'}]},
        {'name': 'graph_2', 'urls': [{'url':'posts_count_daily', 'data_x':'day', 'data_y':'count_posts'},
                                     {'url':'posts_count_new_users','data_x':'day', 'data_y':'count_post'}]},
        {'name': 'graph_3', 'urls': [{'url':'count_comments_weekly', 'data_x':'day', 'data_y':'count_comments'},
                                     {'url':'count_votes_weekly', 'data_x':'day', 'data_y':'count_votes'}]},
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
                        api_query=self.api_query
                )
                res_graph_one.append(data)
            res_all_graphs.append(res_graph_one)
        return res_all_graphs


    def get(self, request):

        data = self.get_data()
        print(data)
        import pdb
        pdb.set_trace()
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

        return render(request, self.template_name, data)