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
    ('1', 'Понедельник'),
    ('2', 'Вторник'),
    ('3', 'Среда'),
    ('4', 'Четверг'),
    ('5', 'Пятница'),
    ('6', 'Суббота'),
]

class CourseModel(models.Model):
    course_name = models.CharField(max_length=100, unique=True)
    weekdays = MultiSelectField(choices=WEEKDAY_CHOICES)
    subject = models.ForeignKey(SubjectModel, on_delete=models.CASCADE)
    teacher = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': '1'})
    start_date = models.DateField()
    lesson_time = models.TimeField()
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


