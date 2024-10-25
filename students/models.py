from django.db import models


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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'student'
        verbose_name_plural = 'students'
        ordering = ['last_name', 'first_name'] 