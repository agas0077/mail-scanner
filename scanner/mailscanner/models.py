# Third Party Library
from apscheduler.jobstores.base import JobLookupError
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from mailscanner.apps import MailscannerConfig
from mailscanner.utils import launch_mail_monitor

User = get_user_model()

IMAP_SERVER_NAME = "Адрес IMAP сервера"
EMAIL_NAME = "Адрес проверяемой почты"
EMAIL_KEY_NAME = "Ключ к почтовому ящику"
SUBJECT_NAME = "Тема письма"
SENDER_NAME = "Отправитель"
SEARCH_STRING_NAME = "Поисковый запрос IMAP"
TASK_NAME_NAME = "Название задания"
DESCRIPTION_NAME = "Описание задания"
JOB_ID_NAME = "Идентификатор задачи"
STATUS_NAME = "Статус"
TRIGGER_NAME = "Триггер"
NEXT_RUN_NAME = "Следующий запуск"

YEAR_NAME = "Год (YYYY)"
MONTH_NAME = "Месяц (1-12)"
DAY_NAME = "День (1-31)"
WEEK_NAME = "Неделя ISO (1-53)"
DAY_OF_WEEK_NAME = "День недели (0-6; 0=понедельник)"
HOUR_NAME = "Часы (0-23)"
MINUTE_NAME = "Минуты (0-59)"
SECOND_NAME = "Секунды (0-59)"
SEC_INTERVAL_NAME = "Интервал в секундах"


class Task(models.Model):
    class Status(models.IntegerChoices):
        INACTIVE = 0, "Остановлено"
        ACTIVE = 1, "Активно"

    class Triggers(models.TextChoices):
        INTERVAL = "interval", "Интервал"
        CRON = "cron", "Кастомный"

    imap_server = models.CharField(IMAP_SERVER_NAME, max_length=50)
    email = models.EmailField(EMAIL_NAME)
    email_key = models.CharField(EMAIL_KEY_NAME, max_length=30)
    task_name = models.CharField(TASK_NAME_NAME, max_length=200)
    description = models.TextField(DESCRIPTION_NAME, blank=True, null=True)
    subject = models.CharField(SUBJECT_NAME, max_length=300)
    sender = models.CharField(SENDER_NAME, max_length=100)
    search_string = models.TextField(
        SEARCH_STRING_NAME, blank=True, null=True, editable=False
    )
    trigger = models.CharField(
        TRIGGER_NAME,
        max_length=20,
        choices=Triggers.choices,
        default=Triggers.INTERVAL,
    )

    year = models.CharField(
        YEAR_NAME, blank=True, null=True, default=None, max_length=30
    )
    month = models.CharField(
        MONTH_NAME, blank=True, null=True, default=None, max_length=30
    )
    day = models.CharField(
        DAY_NAME, blank=True, null=True, default=None, max_length=30
    )
    week = models.CharField(
        WEEK_NAME, blank=True, null=True, default=None, max_length=30
    )
    day_of_week = models.CharField(
        DAY_OF_WEEK_NAME, blank=True, null=True, default=None, max_length=30
    )
    hour = models.CharField(
        HOUR_NAME, blank=True, null=True, default=None, max_length=30
    )
    minutes = models.CharField(
        MINUTE_NAME, blank=True, null=True, default=None, max_length=30
    )
    seconds = models.CharField(
        SECOND_NAME, blank=True, null=True, default=None, max_length=30
    )
    sec_interval = models.PositiveIntegerField(
        SEC_INTERVAL_NAME, blank=True, null=True
    )

    job_id = models.CharField(
        JOB_ID_NAME, max_length=40, blank=True, null=True, editable=False
    )
    status = models.PositiveSmallIntegerField(
        STATUS_NAME, choices=Status.choices, default=Status.INACTIVE
    )
    next_run = models.DateTimeField(
        NEXT_RUN_NAME,
        editable=False,
        blank=True,
        null=True,
    )

    def add_job(self):
        scheduler = MailscannerConfig.scheduler

        if self.job_id:
            try:
                scheduler.remove_job(self.job_id)
            except JobLookupError:
                pass
            finally:
                self.job_id = None

        options = {
            "kwargs": {
                "server": self.imap_server,
                "email": self.email,
                "password": self.email_key,
                "search_string": self.search_string,
            }
        }
        if self.trigger == Task.Triggers.CRON.value:
            options["year"] = self.year
            options["month"] = self.month
            options["day"] = self.day
            options["week"] = self.week
            options["day_of_week"] = self.day_of_week
            options["hour"] = self.hour
            options["minute"] = self.minutes
            options["second"] = self.seconds
        elif self.trigger == Task.Triggers.INTERVAL.value:
            options["seconds"] = self.sec_interval

        job = scheduler.add_job(
            launch_mail_monitor,
            trigger=self.trigger,
            **options,
        )
        return job

    def _get_search_string(self):
        """
        Возвращает строку поиска для задачи, основанную
        на ее теме и отправителе.
        """
        return f'((SUBJECT "{self.subject}") (FROM "{self.sender}"))'

    def save(self, *args, **kwargs) -> None:
        """
        Переопределяет метод save() модели Django.
        Устанавливает строку поиска для задачи на основе
        ее темы и отправителя.
        """
        scheduler = MailscannerConfig.scheduler
        self.search_string = self._get_search_string()

        job = scheduler.get_job(self.job_id)
        if not job:
            job = self.add_job()

        self.job_id = job.id

        if self.status == Task.Status.INACTIVE.value:
            scheduler.pause_job(self.job_id)

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Возвращает строковое представление задачи.
        """
        return self.task_name
