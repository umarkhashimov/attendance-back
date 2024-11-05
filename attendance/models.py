from django.db import models
from courses.models import SessionsModel
from students.models import Enrollment


STATUS_CHOICES = [('1', 'Присутствует'), ('0', 'Отсутствует'), ('3', 'Опоздал')]

class AttendanceModel(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    session = models.ForeignKey(SessionsModel, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.enrollment} - {self.session} - {self.status}"


    class Meta:
        verbose_name = 'attendance record'
        verbose_name_plural = 'attendance records'
        unique_together = ('enrollment', 'session') 
        ordering = ['session__date']