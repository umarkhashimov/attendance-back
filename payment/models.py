from django.db import models
from students.models import Enrollment


class PaymentModel(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name="Запись")
    lessons_covered = models.PositiveIntegerField(default=0, verbose_name="Кол-во покрытых уроков")
    amount = models.FloatField(null=True, verbose_name="Сумма оплаты")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время оплаты")
    status = models.BooleanField(default=False, verbose_name="Статус Оплаты")

    def __str__(self):
        return f"{self.enrollment.student} - {self.enrollment.course.subject}, {self.enrollment.course.course_name}"

    class Meta:
        verbose_name = "payment"
        verbose_name_plural = "payments"