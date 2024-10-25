from django.db import models
from django.contrib.auth.models import AbstractUser

class UsersModel(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'teacher'),
        ('admin', 'admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=13, null=True, blank=True)

    def __str__(self):
        return f"{self.username} - {self.role}"

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
