# Third Party Library
from django.contrib import admin
from mailscanner.models import Task


# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    """Админка модели заданий"""

    list_display = ("task_name",)
    list_filter = ("task_name",)
    readonly_fields = ("search_string", "job_id", "next_run")

    def next_run(self, obj):
        return obj.timefield.strftime("%d-%m-%Y %HH:%mm:%ss")


admin.site.register(Task, TaskAdmin)
