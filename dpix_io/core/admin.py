from django.contrib import admin

from dpix_io.core.models import Subscribe, TeamMembers, Vanancy, Investors


class SubscribeAdmin(admin.ModelAdmin):
    search_fields = ['email']
    fields = ['email', 'created_at']
    ordering = ['-created_at']
    list_display = ['email', 'created_at']

    def has_add_permission(self, request):
        return False


class TeamMembersAdmin(admin.ModelAdmin):
    list_filter = ['last_name']


class VanancyAdmin(admin.ModelAdmin):
    list_filter = ['title']


class InvestorsAdmin(admin.ModelAdmin):
    list_filter = ['email']

admin.site.register(Subscribe, SubscribeAdmin)
admin.site.register(TeamMembers, TeamMembersAdmin)
admin.site.register(Vanancy, VanancyAdmin)
admin.site.register(Investors, InvestorsAdmin)
