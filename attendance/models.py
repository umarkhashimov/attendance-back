from django.db import models
from courses.models import SessionsModel
from students.models import Enrollment


class AttendanceModel(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    session = models.ForeignKey(SessionsModel, on_delete=models.CASCADE)
    status = models.BooleanField(null=True) 
    homework_grade = models.IntegerField(null=True)
    participation_grade = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.enrollment} - {self.session} - {self.status}"


    class Meta:
        verbose_name = 'attendance record'
        verbose_name_plural = 'attendance records'
        unique_together = ('enrollment', 'session') 
        ordering = ['-id']