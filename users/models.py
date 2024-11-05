from django.db import models
from django.contrib.auth.models import AbstractUser

class UsersModel(AbstractUser):
    ROLE_CHOICES = [
        ('1', 'Teacher'),
        ('2', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='1')
    phone_number = models.CharField(max_length=13, null=True, blank=True)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
