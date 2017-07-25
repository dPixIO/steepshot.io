from django.contrib import messages
from django.shortcuts import render
from django.views.generic import TemplateView, View
import requests
from piston import Steem
from piston.converter import Converter
from steepshot_io.core.forms import SubscribeForm


class IndexView(TemplateView):
    template_name = 'index.html'
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        form = SubscribeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'You have successfully subscribed!')
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        kwargs['form'] = SubscribeForm()
        return super(IndexView, self).get_context_data(**kwargs)


def get_steem_per_mvests(steem):
    s = Converter(steem)
    return s.steem_per_mvests()


def get_steem_rate(currencies):
    res = requests.get('https://graphs.coinmarketcap.com/currencies/{}/'.format(currencies)).json()
    return res['price_usd'][-1][1]


def convert_vests_in_usd(vests, steem_per_mvests, steem_rate):
    res = vests * steem_per_mvests / 1000000 * steem_rate
    return res


class GetPostFee(View):
    template_name = 'fee_posts.html'

    def get_fee_posts(self, currency=None):

        if currency == 'usd':
            currencies = 'steem'
            steem_obj = Steem()
            steem_per_mvests = get_steem_per_mvests(steem_obj)
            steem_rate = get_steem_rate(currencies)
        values = []
        res = requests.get('https://qa.steepshot.org/api/v1/posts/fee/daily').json()
        res.reverse()
        for i in res:
            if currency == 'usd':
                val = convert_vests_in_usd(i['count_fee'], steem_per_mvests, steem_rate)
                values.append([i['day'], val])
            else:
                values.append([i['day'],  i['count_fee']])
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