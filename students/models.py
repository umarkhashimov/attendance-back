import datetime

from django.db import models
from courses.models import CourseModel
from django.core.validators import MaxValueValidator
from django.utils import timezone
from users.models import UsersModel
from .helpers import calculate_balance

class StudentModel(models.Model):
    student_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True, editable=False)
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона родителя')
    additional_number = models.CharField(max_length=15, verbose_name='Номер телефона ученика', null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name='Заметка')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')  # Date the student was enrolled
    courses = models.ManyToManyField(CourseModel, through='Enrollment', verbose_name='Записанные курсы')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def in_debt(self):
        overdue_enrollments_count = Enrollment.objects.filter(student=self, payment_due__lt=datetime.datetime.today().date(), status=True).count()
        return overdue_enrollments_count > 0

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'ученик'
        verbose_name_plural = 'ученики'
        ordering = ['-id'] 


class Enrollment(models.Model):
    
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, verbose_name="Студент")
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, verbose_name="Курс", limit_choices_to={'status': True})
    status = models.BooleanField(default=True, verbose_name="Статус Активности")
    trial_lesson = models.BooleanField(default=True, verbose_name="Пробный урок")
    hold = models.PositiveIntegerField(default=0, null=True, verbose_name="Заморозка")
    discount = models.PositiveIntegerField(default=0, verbose_name="Скидка %", validators=[MaxValueValidator(100)])
    debt_note = models.CharField(max_length=200, null=True, blank=True, verbose_name="Заметка для учителя")
    note = models.CharField(max_length=200, null=True, blank=True, verbose_name="Заметка")
    payment_due = models.DateField(null=True, blank=True, verbose_name="Оплачно до")
    enrolled_by = models.ForeignKey(UsersModel, on_delete=models.CASCADE, limit_choices_to={'role': '2'}, null=True, blank=True, verbose_name='Кем записан')
    enrolled_at = models.DateField(auto_now_add=True, verbose_name="Дата записи")

    def __str__(self):
        return f"{self.student} - {self.course}"

    def in_debt(self):
        if self.payment_due:
            return self.payment_due < datetime.date.today()
        return False

    @property
    def balance(self):
        if self.payment_due:
            return calculate_balance(self.payment_due, self.course)
        else:
            return None

    def calc_session_cost_discount(self):
        # return cost of one session with discount
        cost = self.course.session_cost - ((self.course.session_cost / 100) * self.discount)
        return cost

    class Meta:
        verbose_name = "зачисление"
        verbose_name_plural = "зачислении"
        # unique_together = ("student", "course")
