# Standard Library
from typing import Any

# Third Party Library
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig


class MailscannerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailscanner"
    scheduler = BackgroundScheduler()

    def ready(self) -> None:
        # Third Party Library
        from mailscanner.models import Task

        self.scheduler.start()
        task_list = Task.objects.values_list("id", "status")
        for id, status in task_list:
            task = Task.objects.get(pk=id)
            if status == Task.Status.ACTIVE.value:
                new_job_id = task.add_job().id
                task.job_id = new_job_id
            elif status == Task.Status.INACTIVE.value:
                new_job_id = task.add_job().id
                task.job_id = new_job_id
                self.scheduler.pause_job(new_job_id)
            task.save()
