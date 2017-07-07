from django.contrib import admin

from steepshot_io.core.models import Subscribe


class SubscribeAdmin(admin.ModelAdmin):
    search_fields = ['email']
    fields = ['email', 'created_at']
    ordering = ['-created_at']
    list_display = ['email', 'created_at']

    def has_add_permission(self, request):
        return False

admin.site.register(Subscribe, SubscribeAdmin)
