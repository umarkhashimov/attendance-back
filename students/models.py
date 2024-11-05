from django.db import models
from courses.models import CourseModel


class StudentModel(models.Model):
    student_id = models.PositiveBigIntegerField(null=True, blank=True, unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()  # Date of birth
    phone_number = models.CharField(max_length=15)
    additional_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(max_length=300, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    enrollment_date = models.DateField(auto_now_add=True)  # Date the student was enrolled
    email = models.EmailField(null=True, blank=True)
    balance = models.PositiveIntegerField(null=True, blank=True, default=0)
    courses = models.ManyToManyField(CourseModel, through='Enrollment')

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
