# Third Party Library
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django_tables2 import SingleTableMixin
from mailscanner.apps import MailscannerConfig
from mailscanner.models import Task
from mailscanner.tables import TaskTable

# Create your views here.


class IndexView(SingleTableMixin, ListView):
    model = Task
    table_class = TaskTable
    template_name = "mail_scanner_index.html"


def stop_launch_task(request, task_id):
    task = Task.objects.get(id=task_id)
    job_id = task.job_id
    job_status = task.status
    scheduler = MailscannerConfig.scheduler

    if job_status == Task.Status.ACTIVE.value:
        scheduler.pause_job(job_id)
        new_status = Task.Status.INACTIVE
    else:
        scheduler.resume_job(job_id)
        new_status = Task.Status.ACTIVE

    task.status = new_status
    task.save()

    response = {"status": new_status.value}
    print(scheduler.get_job(job_id))
    return JsonResponse(response)


def delete_task(request, task_id):
    task = Task.objects.get(id=task_id)
    job_id = task.job_id
    scheduler = MailscannerConfig.scheduler

    scheduler.remove_job(job_id)
    task.delete()
    return redirect("mail-scanner:index")


def edit_task(request, task_id):
    pass
