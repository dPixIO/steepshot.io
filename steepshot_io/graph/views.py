import requests
from django.shortcuts import render
from django.views.generic import View


class GetPostFee(View):
    template_name = 'fee_posts.html'

    def get_fee_posts(self, currency='VESTS'):

        res = requests.get('https://qa.steepshot.org/api/v1/posts/fee/daily?currency={}'.format(currency)).json()
        res.reverse()
        values = []
        for i in res:
            values.append([i['day'], i['count_fee']])
        return values

    def get(self, request, *args, **kwargs):
        if 'currency' in request.GET:
            currency = request.GET['currency'].lower()
            values = self.get_fee_posts(currency)
        else:
            values = self.get_fee_posts()
        return render(request, self.template_name, {'values': values})


class GetPostsCountMonthly(View):
    template_name = 'count_posts.html'

    def group_steem_golos(self, list_steem, list_golos):
        res = []
        idx = 0
        while True:
            try:
                res.append([list_steem[idx][0], list_steem[idx][1] + list_golos[idx][1]])
            except IndexError:
                break
            idx += 1
        return res

    def get_posts_count_monthly(self, platform=None):

        if platform == 'steem':
            res = requests.get('https://steepshot.org/api/v1/posts/count/monthly').json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['posts_count']])
            return values
        elif platform =='golos':
            res = requests.get('https://qa.golos.steepshot.org/api/v1/posts/count/monthly').json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['posts_count']])
            return values
        else:
            res_steem = requests.get('https://steepshot.org/api/v1/posts/count/monthly').json()
            res_steem.reverse()
            res_golos = requests.get('https://qa.golos.steepshot.org/api/v1/posts/count/monthly').json()
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i['date_to'], i['posts_count']])
            for i in res_golos:
                values_golos.append([i['date_to'], i['posts_count']])
            steem_golos_value = self.group_steem_golos(values_steem, values_golos)

            return steem_golos_value

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_posts_count_monthly(platform=platform)
        else:
            values = self.get_posts_count_monthly()
        return render(request, self.template_name, {'values': values})


class GetActiveUsers(View, GetPostsCountMonthly):
    template_name = 'active_users.html'

    def get_active_users(self, platform=None):
        if platform == 'steem':
            res = requests.get('https://steepshot.org/api/v1/user/active/monthly').json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['active_users']])
            return values
        elif platform == 'golos':
            res = requests.get('https://qa.golos.steepshot.org/api/v1/user/active/monthly').json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['active_users']])
            return values

        else:
            res_steem = requests.get('https://steepshot.org/api/v1/user/active/monthly').json()
            res_steem.reverse()
            res_golos = requests.get('https://qa.golos.steepshot.org/api/v1/user/active/monthly').json()
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i['date_to'], i['active_users']])
            for i in res_golos:
                values_golos.append([i['date_to'], i['active_users']])

            steem_golos_value = self.group_steem_golos(values_steem, values_golos)

            return steem_golos_value

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_active_users(platform=platform)
        else:
            values = self.get_active_users()
        return render(request, self.template_name, {'values': values})


class GetCountPostDaily(View):
    template_name = 'count_post_daily.html'

    def get_count_post_daily(self):
        res = requests.get('https://qa.steepshot.org/api/v1/posts/count/daily').json()
        res.reverse()
        values = []
        for i in res:
            values.append([i['day'], i['count_posts']])
        return values

    def get(self, request):
        values = self.get_count_post_daily()
        return render(request, self.template_name, {'values': values})


class GetRatioDaily(View):
    template_name = 'ratio_daily.html'

    def group_steem_golos(self, list_steem, list_golos):
        res = []
        idx = 0
        while True:
            try:
                res.append([list_steem[idx][0], list_steem[idx][1], list_golos[idx][1]])
            except IndexError:
                break
            idx += 1
        return res

    def get_ratio_daily(self, platform=None):

        if platform == 'steem':
            res = requests.get('https://steepshot.org/api/v1/posts/ratio/daily').json()
            res = res['result']
            res.reverse()
            values = []
            for i in res[:30]:
                values.append([i['date'], i['ratio']])
            return values
        elif platform == 'golos':
            res = requests.get('https://qa.golos.steepshot.org/api/v1/posts/ratio/daily').json()
            res = res['result']
            res.reverse()
            values = []
            for i in res[:30]:
                values.append([i['date'], i['ratio']])
            return values
        else:
            res_steem = requests.get('https://steepshot.org/api/v1/posts/ratio/daily').json()
            res_steem = res_steem['result']
            res_steem.reverse()
            res_golos = requests.get('https://qa.golos.steepshot.org/api/v1/posts/ratio/daily').json()
            res_golos = res_golos['result']
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem[:30]:
                values_steem.append([i['date'], i['ratio']])
            for i in res_golos[:30]:
                values_golos.append([i['date'], i['ratio']])
            return values_steem, values_golos

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_ratio_daily(platform=platform)
            return render(request, self.template_name, {'values': values})

        else:
            values_steem, values_golos = self.get_ratio_daily()
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})


class GetRatioMonthly(GetRatioDaily):
    template_name = 'ratio_monthly.html'

    def get_ratio_monthly(self, platform=None):

        if platform == 'steem':
            res = requests.get('https://steepshot.org/api/v1/posts/ratio/monthly').json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['ratio']])
            return values
        elif platform == 'golos':
            res = requests.get('https://qa.golos.steepshot.org/api/v1/posts/ratio/monthly').json()
            res.reverse()
            values = []
            for i in res:
                values.append([i['date_to'], i['ratio']])
            return values
        else:
            res_steem = requests.get('https://steepshot.org/api/v1/posts/ratio/monthly').json()
            res_steem.reverse()
            res_golos = requests.get('https://qa.golos.steepshot.org/api/v1/posts/ratio/monthly').json()
            res_golos.reverse()
            values_steem = []
            values_golos = []
            for i in res_steem:
                values_steem.append([i['date_to'], i['ratio']])
            for i in res_golos:
                values_golos.append([i['date_to'], i['ratio']])
            return values_steem, values_golos

    def get(self, request, *args, **kwargs):
        if 'platform' in request.GET:
            platform = request.GET['platform'].lower()
            values = self.get_ratio_monthly(platform=platform)
            return render(request, self.template_name, {'values': values})

        else:
            values_steem, values_golos = self.get_ratio_monthly()
            values = self.group_steem_golos(values_steem, values_golos)
            flag_together = True
            return render(request, self.template_name, {'values': values, 'flag': flag_together})