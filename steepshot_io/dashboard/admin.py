from django.contrib import admin
from steepshot_io.dashboard.models import DashboardUsers

# Register your models here.


class DashboardUsersAdmin(admin.ModelAdmin):
    list_filter = ['username']

admin.site.register(DashboardUsers, DashboardUsersAdmin)

