from random import choices

from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.contrib.admin.models import LogEntry, ContentType

class UsersModel(AbstractUser):
    ROLE_CHOICES = [
        ('1', 'Teacher'),
        ('2', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='1')
    phone_number = models.CharField(max_length=13, null=True, blank=True, verbose_name="Номер Телефона")

    @property
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.username} - {self.get_full_name}"

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

def log_user_action(user, obj, action_flag, message):
    LogEntry.objects.log_action(
        user_id=user.id,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=message
    )

ACTION_FLAG_CHOICES = [
    (1, "Создать"),
    (2, "Изменить"),
    (3, "Удалить"),
]

class LogAdminActionsModel(models.Model):
    action_number = models.PositiveSmallIntegerField(choices=ACTION_FLAG_CHOICES)
    user = models.ForeignKey(UsersModel, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    message = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)

    def action_type(self):
        return self.get_action_number_display()