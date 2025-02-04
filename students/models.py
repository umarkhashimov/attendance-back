from django.db import models
from courses.models import CourseModel
from django.core.validators import MaxValueValidator


class StudentModel(models.Model):
    student_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True, editable=False)
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона')
    additional_number = models.CharField(max_length=15, verbose_name='Номер телефона родителей', null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name='Заметка')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Имя')  # Date the student was enrolled
    courses = models.ManyToManyField(CourseModel, through='Enrollment', verbose_name='Записанные курсы')

    def has_debt(self):
        debt_enrollments = Enrollment.objects.all().filter(student=self, balance__lte=0).count()
        if debt_enrollments > 0:
            return True
        return False

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'students'
        ordering = ['-id'] 


class Enrollment(models.Model):
    
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE, verbose_name="Студент")
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, verbose_name="Курс", limit_choices_to={'status': True})
    balance = models.IntegerField(default=0, verbose_name="Баланс")  # Balance per course
    status = models.BooleanField(default=True, verbose_name="Статус Активности")
    trial_lesson = models.BooleanField(default=True, verbose_name="Пробный урок")
    hold = models.PositiveIntegerField(default=0, null=True, verbose_name="Заморозка")
    discount = models.PositiveIntegerField(default=0, verbose_name="Скидка %", validators=[MaxValueValidator(100)])
    debt_note = models.CharField(max_length=100, null=True, blank=True, verbose_name="Заметка должника")

    def __str__(self):
        return f"{self.student} - {self.course}"
    
    def add_balance(self, amount):
        self.balance += amount
        self.save()

    def substract_balance(self, amount):
        self.balance -= amount
        self.save()

    def calc_session_cost_discount(self):
        # return cost of one session with discount
        cost = self.course.session_cost - ((self.course.session_cost / 100) * self.discount)
        return cost
    
    def substract_one_session(self):
        if self.hold > 0:
            self.hold -= 1
        elif self.trial_lesson == True:
            self.trial_lesson = False
        else:
            self.balance -= 1

        self.save()

    class Meta:
        verbose_name = "enrollment"
        verbose_name_plural = "enrollments"
        # unique_together = ("student", "course")
