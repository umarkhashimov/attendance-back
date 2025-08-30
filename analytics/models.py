from django.db import models
from datetime import date
# Create your models here.


class AnalyticsModel(models.Model):
    students = models.PositiveIntegerField(default=0, verbose_name="Кол-во Студентов")
    enrollments = models.PositiveIntegerField(default=0, verbose_name="Кол-во Зачислений")
    trial_enrollments = models.PositiveIntegerField(default=0, verbose_name="Пробники")
    payments = models.PositiveIntegerField(default=0, verbose_name="Оплаты")
    payments_sum = models.FloatField(default=0, verbose_name="Сумма оплат")
    new_students = models.PositiveIntegerField(default=0, verbose_name="Новые Студенты")
    new_enrollments = models.PositiveIntegerField(default=0, verbose_name="Новые Зачисления")
    courses = models.PositiveIntegerField(default=0, verbose_name="Курсы")
    date = models.DateField(default=date.today)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Аналитика'
        verbose_name_plural = 'Аналитика'
        indexes = [models.Index(fields=["date"])]
