from django.contrib import messages
from django.shortcuts import render
from django.views.generic import TemplateView, View
from steepshot_io.core.forms import SubscribeForm
from steepshot_io.core.models import TeamMembers


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

