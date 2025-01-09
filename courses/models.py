from django.db import models
from users.models import UsersModel
from multiselectfield import MultiSelectField
from datetime import timedelta
from django.core.validators import MinValueValidator
from django.utils import timezone

from users.models import UsersModel
from .filters import course_date_match

class SubjectModel(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "subject"
        verbose_name_plural = "subjects"

WEEKDAY_CHOICES = [
    ('0', 'Понедельник'),
    ('1', 'Вторник'),
    ('2', 'Среда'),
    ('3', 'Четверг'),
    ('4', 'Пятница'),
    ('5', 'Суббота'),
]

class CourseModel(models.Model):
    subject = models.ForeignKey(SubjectModel, on_delete=models.CASCADE, verbose_name="предмет")
    course_name = models.CharField(max_length=100, null=True, blank=True, unique=False, verbose_name="имя курса")
    teacher = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': '1'}, verbose_name="учитель")
    weekdays = MultiSelectField(choices=WEEKDAY_CHOICES, verbose_name="дни недели")
    lesson_time = models.TimeField(verbose_name="время урока")
    duration = models.PositiveIntegerField(verbose_name="продолжительность урока (мин)")
    session_cost = models.IntegerField(verbose_name="цена курса за 12 уроков")
    status = models.BooleanField(default=False, verbose_name="Статус курса")

    def __str__(self):
        return f"#{self.id} - {self.course_name}"
    
    def check_time(self):
        return course_date_match(self)
    
    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        ordering = ['id']



class SessionsModel(models.Model):
    CAUSE_OPTIONS = [
        ("1", 'Праздник'),
        ("2", 'Вина Учебного центра')
    ]
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, verbose_name="Курс")
    date = models.DateField(verbose_name="Дата")
    status = models.BooleanField(default=True, verbose_name="Статус проведение урока")
    cause = models.CharField(max_length=50, choices=CAUSE_OPTIONS, null=True)
    record_by = models.ForeignKey(UsersModel, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Кем Отмечено")

    def conduct(self):
        self.status = True
        self.save()

    def __str__(self):
        return f"{self.course.course_name} - Session on {self.date}"

    class Meta:
        verbose_name = 'session'
        verbose_name_plural = 'sessions'
        unique_together = ('course', 'date')
        ordering = ['course__id']
