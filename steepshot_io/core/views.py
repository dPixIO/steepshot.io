from django.shortcuts import render
from django.views.generic import TemplateView

from steepshot_io.core.forms import SubscribeForm


class IndexView(TemplateView):
    template_name = 'index.html'
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        form = SubscribeForm(request.POST)
        if form.is_valid():
            form.save()
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        kwargs['form'] = SubscribeForm()
        return super(IndexView, self).get_context_data(**kwargs)
