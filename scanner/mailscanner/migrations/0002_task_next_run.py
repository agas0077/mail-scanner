# Generated by Django 4.2.5 on 2023-10-04 15:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mailscanner", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="next_run",
            field=models.DateTimeField(
                blank=True, editable=False, null=True, verbose_name="Следующий запуск"
            ),
        ),
    ]
