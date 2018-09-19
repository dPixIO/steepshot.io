import datetime

import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View

from steepshot_io.table_stats.helpers import str_from_datetime, group_data


class TableStatsBaseView(View):
    stats_urls = None

    def _sort_data(self, data):
        data_check = []
        res = {}
        for i in data:
            data_x = i['data_x']
            data_y = i['data_y']
            for j in i['data']:
                key = j[data_y]
                if key in res:
                    res[key].append(j[data_x])
                else:
                    res[key] = [key, j[data_x]]
                    data_check.append(key)

        return sorted(res.items(), key=lambda x: x[0])

    def table_header_build(self):
        res = [i['name_data'].capitalize() for i in self.stats_urls]
        res.insert(0, 'Date')
        return res


class GetStatsTable(TableStatsBaseView):
    template_name = 'table_stats.html'

    stats_urls = [
        {'url': 'count_votes_weekly', 'name_data': 'count votes', 'data_x': 'count_votes', 'data_y': 'day'},
        {'url': 'count_comments_weekly', 'name_data': 'count comments', 'data_x': 'count_comments', 'data_y': 'day'},
        {'url': 'posts_count_daily', 'name_data': 'posts counts', 'data_x': 'count_posts', 'data_y': 'day'},
    ]

    def _get_data_from_request(self):
        date_to = str_from_datetime(datetime.datetime.today())
        date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=30))
        res_golos = []
        res_steem = []
        for i in self.stats_urls:
            url_steem = settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.STEEM_V1)
            req_steem = requests.get(url_steem, params={'date_to': date_to, 'date_from': date_from}).json()
            url_golos = settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.GOLOS_V1)
            req_golos = requests.get(url_golos, params={'date_to': date_to, 'date_from': date_from}).json()
            res_steem.append(dict(data_x=i['data_x'], data_y=i['data_y'], data=req_steem))
            res_golos.append(dict(data_x=i['data_x'], data_y=i['data_y'], data=req_golos))
        return res_steem, res_golos

    def general_stats_build(self, list_1, list_2):
        res = []
        idx = 0
        while True:
            try:
                res.append(group_data(list_1[idx], list_2[idx]))
            except IndexError:
                break
            idx += 1
        return res

    def get(self, request):
        steem_data, golos_data = self._get_data_from_request()
        heder_table = self.table_header_build()
        steem_data = self._sort_data(steem_data)
        golos_data = self._sort_data(golos_data)
        golos_steem_data = self.general_stats_build(steem_data, golos_data)
        list_tables = [{'table_data': golos_steem_data, 'title_table': 'General stats'},
                       {'table_data': steem_data, 'title_table': 'Steem stats'},
                       {'table_data': golos_data, 'title_table': 'Golos stats'}]
        return render(request, self.template_name, {'list_tables': list_tables,
                                                    'heder_table': heder_table})


class GetDelegatorsSteepshot(View):
    template_name = 'delegators_table.html'

    def get(self, request):
        name_url = 'delegators_steepshot'
        url_steem = settings.REQUESTS_URL.get(name_url, '{url}').format(url=settings.STEEM_V1)
        req_steem = requests.get(url_steem, params=request.GET).json()
        res_data = [
            {
                'participation_vests': req_steem[i]['participation_vests'],
                'participation_steem': req_steem[i]['participation_steem'],
                'username': i
            }for i in sorted(req_steem, key=lambda x: req_steem[x]['participation_vests'], reverse=True)]
        header_table = ['№', 'username', 'participation_vests', 'participation_steem']

        return render(request, self.template_name, {'data': res_data,
                                                    'header_table': header_table})


class InstagramTableStatsView(TableStatsBaseView):
    template_name = 'instagram_table.html'

    stats_urls = [
        {'url': 'DAU', 'name_data': 'DAU', 'data_x': 'active_users', 'data_y': 'day'},
        {'url': 'instagram_users_number', 'name_data': 'users number', 'data_x': 'users_number', 'data_y': 'day'},
        {'url': 'instagram_new_users_number', 'name_data': 'users new number', 'data_x': 'users_number', 'data_y': 'day'},
        {'url': 'instagram_posts_number', 'name_data': 'posts number', 'data_x': 'posts_number', 'data_y': 'day'},
        {'url': 'instagram_posts_average', 'name_data': 'posts average per user', 'data_x': 'posts_number', 'data_y': 'day'},
        {'url': 'instagram_posts_payout', 'name_data': 'posts payout', 'data_x': 'payout', 'data_y': 'day'},
        {'url': 'instagram_posts_payout_average', 'name_data': 'posts payout', 'data_x': 'payout', 'data_y': 'day'},
        {'url': 'instagram_voters_number', 'name_data': 'voters number', 'data_x': 'voters_number', 'data_y': 'day'},
        {'url': 'instagram_voters_average', 'name_data': 'voters average per post', 'data_x': 'voters_number', 'data_y': 'day'},
    ]

    def _get_data(self):
        res = []
        date_to = str_from_datetime(datetime.datetime.today())
        date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=30))
        for i in self.stats_urls:
            url_steem = settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.STEEM_V1)
            req = requests.get(url_steem, params={'date_to': date_to, 'date_from': date_from}).json()
            res.append(dict(data_x=i['data_x'], data_y=i['data_y'], data=req))
        return res

    def get(self, request, *args, **kwargs):
        table_header = self.table_header_build()
        data = self._get_data()
        data = self._sort_data(data)
        return render(request, self.template_name, {'table': data,
                                                    'title:': 'Instagram stats',
                                                    'table_header': table_header})
