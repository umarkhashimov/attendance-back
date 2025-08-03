import datetime

from django.db import models
from courses.models import CourseModel
from django.core.validators import MaxValueValidator
from django.utils import timezone
from users.models import UsersModel
from .helpers import calculate_balance
from payment.helpers import next_closest_session_date

class StudentModel(models.Model):
    student_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True, editable=False)
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона родителя')
    additional_number = models.CharField(max_length=15, verbose_name='Номер телефона ученика', null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name='Заметка')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Дата создания')  # Date the student was enrolled
    courses = models.ManyToManyField(CourseModel, through='Enrollment', verbose_name='Записанные курсы')
    archived = models.BooleanField(default=False)

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
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, verbose_name="Курс")
    status = models.BooleanField(default=True, verbose_name="Статус Активности")
    trial_lesson = models.BooleanField(default=True, verbose_name="Пробный урок")
    trail_used_once = models.BooleanField(default=False)
    trail_used_once_date = models.DateField(null=True, blank=True)
    hold = models.BooleanField(default=False, verbose_name="Заморозка")
    discount = models.PositiveIntegerField(default=0, verbose_name="Скидка %", validators=[MaxValueValidator(100)])
    debt_note = models.CharField(max_length=200, null=True, blank=True, verbose_name="Заметка для учителя")
    note = models.CharField(max_length=200, null=True, blank=True, verbose_name="Заметка")
    payment_due = models.DateField(null=True, blank=True, verbose_name="Оплачно до")
    enrolled_by = models.ForeignKey(UsersModel, on_delete=models.CASCADE, limit_choices_to={'role': '2'}, null=True, blank=True, verbose_name='Кем записан')
    transferred = models.BooleanField(default=False)
    transferred_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    enrolled_at = models.DateTimeField(verbose_name="Дата записи", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.course}"

    def in_debt(self):
        if self.payment_due:
            return self.payment_due < datetime.date.today()
        else:
            return True

    @property
    def balance(self):
        return calculate_balance(self)

    def calculate_new_payment_due(self, new_weekdays, balance=None):
        current_date = datetime.date.today()
        old_balance = self.balance if balance is None else balance
        negative = old_balance < 0

        if old_balance == 0:

            max_iterations = 7
            while max_iterations > 0:

                if str(current_date.weekday()) in new_weekdays:
                    next_date = current_date
                    self.payment_due = next_date - datetime.timedelta(days=1)
                    break

                current_date += datetime.timedelta(days=1)
                max_iterations -= 1

            self.save()
            return None

        if negative:
            current_date -= datetime.timedelta(days=1)

        count = 0
        while count < abs(old_balance):

            if str(current_date.weekday()) in new_weekdays:
                count += 1

                if count >= abs(old_balance):
                    break

            current_date += datetime.timedelta(days=-1 if negative else 1)


        self.payment_due = current_date
        self.save()


    def calc_session_cost_discount(self):
        # return cost of one session with discount
        cost = self.course.session_cost - ((self.course.session_cost / 100) * self.discount)
        return cost

    class Meta:
        verbose_name = "зачисление"
        verbose_name_plural = "зачислении"
        # unique_together = ("student", "course")
        ordering = ['-enrolled_at', 'student__first_name', 'student__last_name']