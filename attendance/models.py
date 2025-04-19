from django.db import models
from courses.models import SessionsModel
from students.models import Enrollment


class AttendanceModel(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    session = models.ForeignKey(SessionsModel, on_delete=models.CASCADE)
    # status = models.BooleanField(blank=True, null=True)
    status = models.IntegerField(choices=[(1, 'Присутствует'), (0, "Отсутствует"), (2, "Опоздал")], null=True, blank=True)
    homework_grade = models.IntegerField(null=True, blank=True)
    participation_grade = models.IntegerField(null=True, blank=True)
    trial_attendance = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.enrollment} - {self.session} - {self.status}"


    class Meta:
        verbose_name = 'посещение'
        verbose_name_plural = 'посещении'
        unique_together = ('enrollment', 'session') 
        ordering = [ '-enrollment__trial_lesson', '-trial_attendance','enrollment__student__first_name', 'enrollment__student__last_name']