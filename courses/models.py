from django.db import models
from users.models import UsersModel
from multiselectfield import MultiSelectField
from datetime import timedelta

from .filters import session_date_match

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
    start_date = models.DateField(verbose_name="начало курса/группы")
    duration = models.PositiveIntegerField(verbose_name="продолжительность урока (мин)")
    total_lessons = models.PositiveIntegerField(verbose_name="кол-во уроков")
    session_cost = models.PositiveIntegerField(default=0, verbose_name="цена урока")
    is_started = models.BooleanField(default=False, verbose_name="курс начался")
    finished = models.BooleanField(default=False, verbose_name="курс закончен")

    def __str__(self):
        return self.course_name
    

    def create_sessions(self):
        lesson_days = [i for i in self.weekdays]
        current_date = self.start_date
        created_count = 0
        if self.is_started == False:
            while created_count < self.total_lessons:
                if str(current_date.weekday()) in lesson_days:
                    SessionsModel.objects.create(course=self, date=current_date, session_number=created_count + 1,)
                    print('created session: ', current_date.strftime("%A, %B %d, %Y"), current_date.weekday())
                    created_count += 1
                
                current_date += timedelta(days=1)
            self.is_started =  True
            self.save()

    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        ordering = ['id']



class SessionsModel(models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    session_number = models.PositiveIntegerField()
    date = models.DateField()
    is_canceled = models.BooleanField(default=False)
    conducted = models.BooleanField(default=False)

    def conduct(self):
        self.conducted = True
        self.save()

    @property
    def check_time(self):
        return session_date_match(self)

    def __str__(self):
        return f"{self.course.course_name} - Session {self.session_number} on {self.date}"

    class Meta:
        verbose_name = 'session'
        verbose_name_plural = 'sessions'
        unique_together = ('course', 'session_number')
        ordering = ['course__id']
