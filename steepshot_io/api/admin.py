from django.contrib import admin

from steepshot_io.api.models import WorkRequest


@admin.register(WorkRequest)
class WorkRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'project_name', 'duration', 'urgency')
