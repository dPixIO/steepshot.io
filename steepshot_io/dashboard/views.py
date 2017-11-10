import datetime
import requests
from django.conf import settings
from django.shortcuts import render
from django.views.generic import View


class GetDashboard(View):
    template_name = 'table_stats.html'

    def get(self, request):
        return render(request, self.template_name)