from django.db import models

from students.models import StudentModel, Enrollment
from users.models import UsersModel
from courses.models import SubjectModel

class LeadsModel(models.Model):
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, verbose_name="Ученик")
    weekdays = models.IntegerField(choices=[(1, "Нечетные"), (2, "Четные"), (3, "Другие")], null=True, blank=True, verbose_name="Дни уроков")
    lesson_time = models.TimeField(verbose_name="время урока", null=True, blank=True)
    subject = models.ForeignKey(SubjectModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Предмет")
    teacher = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': '1', 'is_active': True}, verbose_name="учитель")
    arrival_date = models.DateField(null=True, blank=True, verbose_name="Примерная дата")
    note = models.TextField(null=True, blank=True, max_length=500, verbose_name="Заметка")
    status = models.IntegerField(choices=[(1, "Ожидание"), (2, "Обработан"), (3, "Отменен")], default=1)
    processed_date = models.DateField(null=True, blank=True)
    enrollment_result = models.ForeignKey(Enrollment, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_by')
    processed_by = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_by')
    processed_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'лид'
        verbose_name_plural = 'лиды'
