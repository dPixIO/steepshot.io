"""dpix_io URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(settings.ADMIN_URL, admin.site.urls),
    url(r'', include('dpix_io.core.urls', namespace="core")),
    url(r'^api/', include('dpix_io.api.urls', namespace="api")),
    url(r'^graph/', include('dpix_io.graph.urls', namespace="graph")),
    url(r'^table/', include('dpix_io.table_stats.urls', namespace="table_stats")),
    url(r'^dashboard/', include('dpix_io.dashboard.urls', namespace="dashboard")),
]
