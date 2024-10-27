from django.db import models
from students.models import Enrollment


class Payment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    lessons_covered = models.IntegerField(default=0)  # Number of lessons covered by this payment

    def save(self, *args, **kwargs):
        # Update enrollment balance and lessons paid
        self.enrollment.balance += self.amount
        self.enrollment.lessons_paid += self.lessons_covered
        self.enrollment.save()
        super().save(*args, **kwargs)
