import datetime
from django.shortcuts import render
from steepshot_io.graph.views import BaseView
from steepshot_io.table_stats.helpers import str_from_datetime
from steepshot_io.graph.data_modifiers import SumModifier


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

    def get_data(self, api_query=None):
        if not api_query:
            api_query = self.api_query
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
                        api_query=api_query
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
        # data = self.get_data()
        # data_graphs = self._group_data(data)
        data_graphs = [{'headers': [{'Date': 'string'}, {'DAY': 'number'}, {'DAY new users': 'number'}], 'title': 'DAY and DAY new users', 'data_sum': [['2017-11-06', 193, 0], ['2017-11-07', 170, 0], ['2017-11-08', 188, 0], ['2017-11-09', 190, 0], ['2017-11-10', 173, 0], ['2017-11-11', 199, 0], ['2017-11-12', 215, 0]], 'data_steem': [['2017-11-06', 173, 0], ['2017-11-07', 156, 0], ['2017-11-08', 167, 0], ['2017-11-09', 170, 0], ['2017-11-10', 156, 0], ['2017-11-11', 174, 0], ['2017-11-12', 196, 0]], 'data_golos': [['2017-11-06', 20, 0], ['2017-11-07', 14, 0], ['2017-11-08', 21, 0], ['2017-11-09', 20, 0], ['2017-11-10', 17, 0], ['2017-11-11', 25, 0], ['2017-11-12', 19, 0]]}, {'headers': [{'Date': 'string'}, {'Count posts': 'number'}, {'Count post new users': 'number'}], 'title': 'Count posts and count post from new users', 'data_sum': [['2017-11-06', 225, 0], ['2017-11-07', 146, 0], ['2017-11-08', 171, 0], ['2017-11-09', 169, 0], ['2017-11-10', 173, 0], ['2017-11-11', 187, 0], ['2017-11-12', 208, 0]], 'data_steem': [['2017-11-06', 208, 0], ['2017-11-07', 144, 0], ['2017-11-08', 159, 0], ['2017-11-09', 161, 0], ['2017-11-10', 162, 0], ['2017-11-11', 179, 0], ['2017-11-12', 203, 0]], 'data_golos': [['2017-11-06', 17, 0], ['2017-11-07', 2, 0], ['2017-11-08', 12, 0], ['2017-11-09', 8, 0], ['2017-11-10', 11, 0], ['2017-11-11', 8, 0], ['2017-11-12', 5, 0]]}, {'headers': [{'Date': 'string'}, {'Count comments': 'number'}, {'Count votes': 'number'}], 'title': 'Count comments and count votes', 'data_sum': [['2017-11-06', 33, 286], ['2017-11-07', 41, 295], ['2017-11-08', 31, 372], ['2017-11-09', 23, 263], ['2017-11-10', 11, 328], ['2017-11-11', 40, 567], ['2017-11-12', 47, 580]], 'data_steem': [['2017-11-06', 33, 280], ['2017-11-07', 41, 288], ['2017-11-08', 29, 323], ['2017-11-09', 22, 245], ['2017-11-10', 11, 312], ['2017-11-11', 38, 552], ['2017-11-12', 47, 574]], 'data_golos': [['2017-11-06', 0, 6], ['2017-11-07', 0, 7], ['2017-11-08', 2, 49], ['2017-11-09', 1, 18], ['2017-11-10', 0, 16], ['2017-11-11', 2, 15], ['2017-11-12', 0, 6]]}]
        check_platform = {'steem': True, 'golos': False, 'sun': False}
        return render(request, self.template_name, {'data': data_graphs, 'check_platform': check_platform})

    def post(self, request):
        import pdb
        pdb.set_trace()
        # if request.POST.get('date'):
        #     date_api = request.POST.get('date')
        #     if date_api == '6':
        #         days = 30
        #         months = 6
        #         date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=days * months))
        #         api_query = {'date_to': self.date_to, 'date_from': date_from}
        #     elif date_api == '30':
        #         date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=30))
        #         api_query = {'date_to': self.date_to, 'date_from': date_from}
        #     else:
        #         api_query = self.api_query
        #     data = self.get_data(api_query=api_query)
        #     data_graphs = self._group_data(data)
        #     check_platform = {'steem': True, 'golos': False, 'sun': False}
        #     return render(request, self.template_name, {'data': data_graphs, 'check_platform': check_platform})
        # platform = request.POST.get('myRadio')
        # if platform == 'steem':
        #     check_platform = {'steem': True, 'golos': False, 'sun': False}
        # elif platform == 'golos':
        #     check_platform = {'steem': False, 'golos': True, 'sun': False}
        # else:
        #     check_platform = {'steem': False, 'golos': False, 'sun': True}
        # # # graphs = [{'headers': [{'Date': 'string'}, {'DAY': 'number'}, {'DAY new users': 'number'}], 'title': 'DAY and DAY new users', 'data_sum': [['2017-11-06', 193, 0], ['2017-11-07', 170, 0], ['2017-11-08', 188, 0], ['2017-11-09', 190, 0], ['2017-11-10', 173, 0], ['2017-11-11', 199, 0], ['2017-11-12', 215, 0]], 'data_steem': [['2017-11-06', 173, 0], ['2017-11-07', 156, 0], ['2017-11-08', 167, 0], ['2017-11-09', 170, 0], ['2017-11-10', 156, 0], ['2017-11-11', 174, 0], ['2017-11-12', 196, 0]], 'data_golos': [['2017-11-06', 20, 0], ['2017-11-07', 14, 0], ['2017-11-08', 21, 0], ['2017-11-09', 20, 0], ['2017-11-10', 17, 0], ['2017-11-11', 25, 0], ['2017-11-12', 19, 0]]}, {'headers': [{'Date': 'string'}, {'Count posts': 'number'}, {'Count post new users': 'number'}], 'title': 'Count posts and count post from new users', 'data_sum': [['2017-11-06', 225, 0], ['2017-11-07', 146, 0], ['2017-11-08', 171, 0], ['2017-11-09', 169, 0], ['2017-11-10', 173, 0], ['2017-11-11', 187, 0], ['2017-11-12', 208, 0]], 'data_steem': [['2017-11-06', 208, 0], ['2017-11-07', 144, 0], ['2017-11-08', 159, 0], ['2017-11-09', 161, 0], ['2017-11-10', 162, 0], ['2017-11-11', 179, 0], ['2017-11-12', 203, 0]], 'data_golos': [['2017-11-06', 17, 0], ['2017-11-07', 2, 0], ['2017-11-08', 12, 0], ['2017-11-09', 8, 0], ['2017-11-10', 11, 0], ['2017-11-11', 8, 0], ['2017-11-12', 5, 0]]}, {'headers': [{'Date': 'string'}, {'Count comments': 'number'}, {'Count votes': 'number'}], 'title': 'Count comments and count votes', 'data_sum': [['2017-11-06', 33, 286], ['2017-11-07', 41, 295], ['2017-11-08', 31, 372], ['2017-11-09', 23, 263], ['2017-11-10', 11, 328], ['2017-11-11', 40, 567], ['2017-11-12', 47, 580]], 'data_steem': [['2017-11-06', 33, 280], ['2017-11-07', 41, 288], ['2017-11-08', 29, 323], ['2017-11-09', 22, 245], ['2017-11-10', 11, 312], ['2017-11-11', 38, 552], ['2017-11-12', 47, 574]], 'data_golos': [['2017-11-06', 0, 6], ['2017-11-07', 0, 7], ['2017-11-08', 2, 49], ['2017-11-09', 1, 18], ['2017-11-10', 0, 16], ['2017-11-11', 2, 15], ['2017-11-12', 0, 6]]}]

        return render(request, self.template_name, {})
