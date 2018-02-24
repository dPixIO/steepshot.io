import requests
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.core.paginator import Paginator
from steepshot_io.core.forms import SubscribeForm, InvestorsForms
from steepshot_io.core.models import TeamMembers, Vanancy


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


class GetFAQ(View):
    template_name = 'faq.html'

    def get(self, request):
        return render(request, self.template_name)


class GetTeam(View):
    template_name = 'team.html'

    def get(self, request):
        team = TeamMembers.objects.all()

        return render(request, self.template_name, {"team": team})


class GetJobs(View):
    template_name = 'jobs.html'

    def get(self, request):
        jobs = Vanancy.objects.all()
        return render(request, self.template_name, {"jobs": jobs})


class GetJob(View):
    template_name = 'job.html'

    def get(self, request, job_id):
        job = Vanancy.objects.get(id=job_id)
        return render(request, self.template_name, {"job": job})


class GetInvestor(View):
    template_name = 'investor.html'

    def get(self, request):
        form = InvestorsForms()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = InvestorsForms(request.POST)
        success = False
        if form.is_valid():
            form.save()
            success = True
            form = InvestorsForms()
        return render(request, self.template_name, {'form': form, 'success': success})


class PostAnalitycs(View):
    template_name = 'post_analitycs.html'
    endpoint = {'url': 'posts_new', 'limit': 20,}

    def _get_data_from_request(self, *args, **kwargs):
        url_steem = settings.REQUESTS_URL.get(self.endpoint['url'], '{url}').format(url=settings.STEEM_V1_1)
        req_steem = requests.get(url_steem, params={'limit': self.endpoint['limit'], 'offset': kwargs['offset']}).json()
        for post in req_steem['results']:
            post['post_url'] = post['url'][post['url'][1:].find('/') + 1:]
        return req_steem

    def get(self, request):
        data_steem = self._get_data_from_request(offset=request.GET.get('offset'))
        context = {'data_steem': data_steem}
        return render(request, self.template_name, context)
