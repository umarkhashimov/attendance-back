from django.db import models
from courses.models import CourseModel


class StudentModel(models.Model):
    student_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True, editable=False)
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)  # Date of birth
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона')
    additional_number = models.CharField(max_length=15, verbose_name='Номер телефона родителей')
    address = models.TextField(max_length=300, blank=True, null=True, verbose_name='Адресс')
    notes = models.TextField(blank=True, null=True, verbose_name='Заметка')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Имя')  # Date the student was enrolled
    balance = models.PositiveIntegerField(null=True, blank=True, default=0, verbose_name='Баланс')
    courses = models.ManyToManyField(CourseModel, through='Enrollment', verbose_name='Записанные курсы')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'students'
        ordering = ['last_name', 'first_name'] 


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('1', 'Active'),
        ('0', 'Dropped'),
    ]
    
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Balance per course
    lessons_paid = models.IntegerField(default=0)  # Total lessons covered by payments
    lessons_attended = models.IntegerField(default=0)  # Lessons attended by student
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='1')  # Enrollment status
    trial_lesson = models.BooleanField(default=False)

    def lessons_remaining(self):
        return max(self.lessons_paid - self.lessons_attended, 0)

    def drop_course(self):
        remaining_lessons = self.lessons_remaining()
        if remaining_lessons > 0:
            # Calculate the refund for remaining lessons
            lesson_cost = self.course.lesson_cost
            refund_amount = remaining_lessons * lesson_cost
            self.balance += refund_amount  # Adjust balance or handle refund separately
        self.status = 'dropped'
        self.save()

    def __str__(self):
        return f"{self.student} - {self.course} ({self.status})"
    
    class Meta:
        verbose_name = "enrollment"
        verbose_name_plural = "enrollments"
        unique_together = ("student", "course")
