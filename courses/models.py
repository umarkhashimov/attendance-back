from django.db import models
from django.conf import settings  # to use custom user model if needed
from users.models import UsersModel
from students.models import StudentModel




class CourseModel(models.Model):
    course_name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    teacher = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    start_date = models.DateField()
    lesson_time = models.TimeField()
    duration = models.TimeField()
    total_lessons = models.PositiveIntegerField()
    students = models.ManyToManyField(StudentModel)
    is_started = models.BooleanField(default=False)
    course_cost = models.PositiveIntegerField(default=0)
    
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
