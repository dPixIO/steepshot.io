import datetime

import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View

from steepshot_io.table_stats.helpers import str_from_datetime, group_data


class GetStatsTable(View):
    template_name = 'table_stats.html'

    name_stats_endpoints = [
        {'url': 'count_votes_weekly', 'name_data': 'count votes', 'data_x': 'count_votes', 'data_y': 'day'},
        {'url': 'count_comments_weekly', 'name_data': 'count comments', 'data_x': 'count_comments', 'data_y': 'day'},
        {'url': 'posts_count_daily', 'name_data': 'posts counts', 'data_x': 'count_posts', 'data_y': 'day'},
    ]

    date_to = str_from_datetime(datetime.datetime.today())
    date_from = str_from_datetime(datetime.datetime.today() - datetime.timedelta(days=30))

    def _get_header_table(self):
        res = [i['name_data'].capitalize() for i in self.name_stats_endpoints]
        res.insert(0, 'Date')
        return res

    def _get_data_from_request(self):
        res_golos = []
        res_steem = []
        for i in self.name_stats_endpoints:
            url_steem = settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.STEEM_V1)
            req_steem = requests.get(url_steem, params={'date_to': self.date_to, 'date_from': self.date_from}).json()
            url_golos = settings.REQUESTS_URL.get(i['url'], '{url}').format(url=settings.GOLOS_V1)
            req_golos = requests.get(url_golos, params={'date_to': self.date_to, 'date_from': self.date_from}).json()
            res_steem.append(dict(data_x=i['data_x'], data_y=i['data_y'], data=req_steem))
            res_golos.append(dict(data_x=i['data_x'], data_y=i['data_y'], data=req_golos))
        return res_steem, res_golos

    def _sort_data(self, list_to_sort):
        check_date = []
        res = {}
        for i in list_to_sort:
            data_x = i['data_x']
            data_y = i['data_y']
            for je in i['data']:
                key = je[data_y]
                if key in check_date:
                    res[key].append(je[data_x])
                else:
                    res[key] = [key, je[data_x]]
                    check_date.append(key)

        return sorted(res.items(), key=lambda key: key[0])

    def _res_golos_steem(self, list_1, list_2):
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
        data_steem, data_golos = self._get_data_from_request()
        heder_table = self._get_header_table()
        data_steem = self._sort_data(data_steem)
        data_golos = self._sort_data(data_golos)
        data_golos_steem = self._res_golos_steem(data_steem, data_golos)
        list_tables = [{'table_data': data_golos_steem, 'title_table': 'General stats'},
                       {'table_data': data_steem, 'title_table': 'Steem stats'},
                       {'table_data': data_golos, 'title_table': 'Golos stats'}]
        return render(request, self.template_name, {'list_tables': list_tables,
                                                    'heder_table': heder_table})


class GetDelegatorsSteepshot(View):
    template_name = 'delegators_table.html'

    def get(self, request):
        name_url = 'delegators_steepshot'
        url_steem = settings.REQUESTS_URL.get(name_url, '{url}').format(url=settings.STEEM_QA_V1)
        req_steem = requests.get(url_steem, params=request.GET).json()
        res_data = [
            {
                'vests_per_hour': req_steem[i]['vests_per_hour'],
                'steem_per_hour': req_steem[i]['steem_per_hour'],
                'username': i
            }for i in sorted(req_steem, key=lambda x: req_steem[x]['vests_per_hour'], reverse=True)]
        header_table = ['№', 'username', 'vests_per_hour', 'steem_per_hour']

        return render(request, self.template_name, {'data': res_data,
                                                    'header_table': header_table})
