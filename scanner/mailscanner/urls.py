# Third Party Library
from django.contrib import admin
from django.urls import path
from mailscanner import views

app_name = "mailscanner"

urlpatterns = [
    path("index/", views.IndexView.as_view(), name="index"),
    path(
        "stop_launch/<int:task_id>", views.stop_launch_task, name="stop_launch"
    ),
    path("edit/<int:task_id>", views.edit_task, name="edit"),
    path("delete/<int:task_id>", views.delete_task, name="delete"),
]
