from django.db import models
from courses.models import CourseModel


class StudentModel(models.Model):
    student_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True, editable=False)
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона')
    additional_number = models.CharField(max_length=15, verbose_name='Номер телефона родителей')
    notes = models.TextField(blank=True, null=True, verbose_name='Заметка')
    enrollment_date = models.DateField(auto_now_add=True, verbose_name='Имя')  # Date the student was enrolled
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
    
    student = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Balance per course
    status = models.BooleanField(default=True)
    trial_lesson = models.BooleanField(default=True)
    hold = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.student} - {self.course} ({self.status})"
    
    class Meta:
        verbose_name = "enrollment"
        verbose_name_plural = "enrollments"
        unique_together = ("student", "course")
