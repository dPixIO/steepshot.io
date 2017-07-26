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

    def get_posts_count_monthly(self):

        res = requests.get('https://steepshot.org/api/v1/posts/count/monthly').json()
        res.reverse()
        values = []
        for i in res:
            values.append([i['date_to'], i['posts_count']])
        return values

    def get(self, request):
        values = self.get_posts_count_monthly()
        return render(request, self.template_name, {'values': values})


class GetActiveUsers(View):
    template_name = 'active_users.html'

    def get_active_users(self):
        res = requests.get('https://steepshot.org/api/v1/user/active/monthly').json()
        res.reverse()
        values = []
        for i in res:
            values.append([i['date_to'], i['active_users']])
        return values

    def get(self, request):
        values = self.get_active_users()
        return render(request, self.template_name, {'values': values})
