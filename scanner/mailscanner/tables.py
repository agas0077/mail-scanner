# Third Party Library
import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from mailscanner.models import Task
from requests import delete


class TaskTable(tables.Table):
    """Настройки основной таблице приложения."""

    edit_button = tables.Column(
        empty_values=(), orderable=False, verbose_name="Действия"
    )

    class Meta:
        model = Task
        fields = ("id", "task_name", "description", "edit_button")
        attrs = {"class": "table table-striped table-hover table-bordered"}
        per_page = 10
        order_by = "-id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render_edit_button(self, record):
        """
        Пересоздает столбец с названиями,
        так чтобы названия были сслыками на редактирование.
        """
        if record.status == Task.Status.INACTIVE.value:
            stop_launch_color = "success"
            stop_launch_text = "Запустить"
        else:
            stop_launch_color = "warning"
            stop_launch_text = "Остановить"

        params = {
            # "edit": [
            #     reverse(
            #         "mail-scanner:edit",
            #         args=[
            #             record.id,
            #         ],
            #     ),
            #     "Изменить",
            #     "primary",
            # ],
            "stop_launch": [
                reverse(
                    "mail-scanner:stop_launch",
                    args=[
                        record.id,
                    ],
                ),
                stop_launch_text,
                stop_launch_color,
            ],
            "delete": [
                reverse(
                    "mail-scanner:delete",
                    args=[
                        record.id,
                    ],
                ),
                "Удалить",
                "danger",
            ],
        }
        strings = []
        for key, val in params.items():
            url, text, color = val
            string = f'<button id="{record.id}" type="button" class="{key} btn btn-{color} me-2" href="{url}">{text}</button>'
            strings.append(string)
        strings = "".join(strings)
        string = f"<div class='d-flex justify-content-end'>{strings}<div>"

        return format_html(string)
