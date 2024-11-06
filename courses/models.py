from typing import Iterable
from django.db import models
from django.conf import settings  # to use custom user model if needed
from users.models import UsersModel
from multiselectfield import MultiSelectField


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
    subject = models.ForeignKey(SubjectModel, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100, null=True, blank=True, unique=False)
    teacher = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': '1'})
    weekdays = MultiSelectField(choices=WEEKDAY_CHOICES)
    lesson_time = models.TimeField()
    start_date = models.DateField()
    duration = models.PositiveIntegerField()
    total_lessons = models.PositiveIntegerField()
    course_cost = models.PositiveIntegerField(default=0)
    is_started = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.course_name

    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        ordering = ['course_name']



class SessionsModel(models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    session_number = models.PositiveIntegerField()
    date = models.DateField()
    is_canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course.course_name} - Session {self.session_number} on {self.date}"

    class Meta:
        verbose_name = 'session'
        verbose_name_plural = 'sessions'
        unique_together = ('course', 'session_number')
        ordering = ['date']


