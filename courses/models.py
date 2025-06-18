from django.db import models
from users.models import UsersModel
from multiselectfield import MultiSelectField
from datetime import timedelta
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.apps import apps

from users.models import UsersModel
from .filters import course_date_match

class SubjectModel(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Имя предмета")
    show_separately = models.BooleanField(default=False, verbose_name="Отображать раздельно")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "предмет"
        verbose_name_plural = "предметы"

WEEKDAY_CHOICES = [
    ('0', 'Понедельник'),
    ('1', 'Вторник'),
    ('2', 'Среда'),
    ('3', 'Четверг'),
    ('4', 'Пятница'),
    ('5', 'Суббота'),
    ('6', 'Воскресенье'),
]

weekdays_short = {
    '0': 'Пн',
    '1': 'Вт',
    '2': 'Ср',
    '3': 'Чт',
    '4': 'Пт',
    '5': 'Сб',
    '6': 'Вс',
}

class CourseModel(models.Model):
    subject = models.ForeignKey(SubjectModel, on_delete=models.CASCADE, verbose_name="предмет")
    course_name = models.CharField(max_length=100, null=True, blank=True, unique=False, verbose_name="имя курса")
    teacher = models.ForeignKey(UsersModel, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': '1', 'is_active': True}, verbose_name="учитель")
    weekdays = MultiSelectField(choices=WEEKDAY_CHOICES, verbose_name="дни недели")
    lesson_time = models.TimeField(verbose_name="время урока")
    duration = models.PositiveIntegerField(verbose_name="длительность урока (мин)")
    session_cost = models.IntegerField(verbose_name="цена курса за 12 уроков")
    last_topic = models.CharField(max_length=250, null=True, blank=True, verbose_name='Тема')
    status = models.BooleanField(default=False, verbose_name="Статус курса")
    enrolled = models.ManyToManyField('students.StudentModel', through="students.Enrollment", editable=False)
    archived = models.BooleanField(default=False, verbose_name="В архиве")
    created_at = models.DateTimeField(auto_now_add=True)

    def archive_course(self):
        if self.get_all_enrolled_count() > 0:
            return False
        else:
            self.archived = True
            self.save()
            return True

    def check_time(self):
        return course_date_match(self)

    def get_all_enrolled_count(self):
        Enrollments = apps.get_model('students', 'Enrollment')
        count = Enrollments.objects.filter(course=self, status=True).count()
        return count

    def get_enrolled_count(self):
        Enrollments = apps.get_model('students', 'Enrollment')
        count = Enrollments.objects.filter(course=self, status=True, trial_lesson=False).count()
        return count

    get_enrolled_count.short_description = 'Кол-во Учеников'

    def get_last_topic(self):
        last_session = SessionsModel.objects.all().filter(course=self, status=True).order_by('date').last()
        topic = last_session.topic if last_session else None 
        return topic

    def set_topic(self):
        self.last_topic = self.get_last_topic()
        self.save()

    def get_name(self):
        course_weekdays = [x for x in self.weekdays]
        weekdays = ','.join(weekdays_short[num] for num in course_weekdays)
        return weekdays

    get_name.short_description = 'Дни занятий'

    def __str__(self):
        return f"{self.id}. {self.get_name()} - {self.lesson_time.strftime(format="%H:%M")}. {self.subject}"
    
    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'
        ordering = ['weekdays', 'lesson_time']


class SessionsModel(models.Model):
    CAUSE_OPTIONS = [
        ("1", 'Праздник'),
        ("2", 'Вина Учебного центра')
    ]
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, verbose_name="Курс")
    date = models.DateField(verbose_name="Дата")
    topic = models.CharField(max_length=250, null=True, blank=True, verbose_name='Тема')
    status = models.BooleanField(default=True, verbose_name="Статус проведение урока")
    cause = models.CharField(max_length=50, choices=CAUSE_OPTIONS, null=True, blank=True)
    record_by = models.ForeignKey(UsersModel, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Кем Отмечено")

    def conduct(self):
        self.status = True
        self.save()

    def __str__(self):
        return f"{self.course} - Дата: {self.date}"

    def has_unmarked_attendance(self):
        attendance_model = apps.get_model('attendance', 'AttendanceModel')
        unmarked_attendance_count = attendance_model.objects.filter(session=self, status=None).count()
        return unmarked_attendance_count > 0

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'
        unique_together = ('course', 'date')
        ordering = ['-id']
