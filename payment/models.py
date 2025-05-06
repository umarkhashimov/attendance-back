from django.db import models
from students.models import Enrollment


class PaymentModel(models.Model):
    MONTHS_CHOICES = [
        (1, "1 Месяц"),
        (2, "2 Месяца"),
        (3, "3 Месяца"),
        (6, "6 Месяца"),
    ]
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name="Запись")
    months = models.PositiveIntegerField(choices=MONTHS_CHOICES, verbose_name="Кол-во месяйев")
    amount = models.FloatField(null=True, blank=True, verbose_name="Сумма оплаты")
    payed_from = models.DateField(null=True, blank=True, verbose_name="Начало абонимента")
    payed_due = models.DateField(null=True, blank=True, verbose_name="Конец абонимента")
    manual_dates = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время оплаты")

    def __str__(self):
        return f"{self.enrollment.student} - {self.enrollment.course.subject}, {self.enrollment.course}"

    class Meta:
        verbose_name = "оплата"
        verbose_name_plural = "оплаты"