from random import choices
import os
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.contrib.admin.models import LogEntry, ContentType
from django.apps import apps
from PIL import Image, ImageOps

PERMISSION_CHOICES = [
    ('delete_enrollment', 'Может удалить ученика из группы'),
    ('re_enrollment', 'Может перемещать запись'),
    ('mark_session', 'Может отмечать уроки (только во время урока)'),
    ('change_attendance', 'Может изменить посещаемость'),
    ('create_payment', 'Может вводить оплату'),
]

def get_default_permissions():
    return [perm[0] for perm in PERMISSION_CHOICES]

def convert_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{:%Y-%m-%d-%H-%M-%S-%f}.{}'.format(datetime.now(), ext)
    return os.path.join('./users', filename)

class UsersModel(AbstractUser):
    ROLE_CHOICES = [
        ('1', 'Учитель'),
        ('2', 'Администратор'),
    ]
    image = models.ImageField(upload_to=convert_file_name, null=True, blank=True, default="img/user.webp")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='1', verbose_name='Роль')
    phone_number = models.CharField(max_length=13, null=True, blank=True, verbose_name="Номер Телефона")
    bio = models.TextField(null=True, blank=True, verbose_name='Биография')
    color = models.CharField(max_length=7, default='#ffffff', null=True, blank=True, verbose_name="Цвет выделения")
    custom_permissions = models.JSONField(default=get_default_permissions(), blank=True, null=True)

    def has_permission(self, permission):
        return permission in self.custom_permissions

    # Store selected permissions as a set of boolean flags
    @property
    def get_full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name or self.last_name:
            return self.first_name or self.last_name
        else:
            return self.username

    @property
    def get_short_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}. {self.last_name}"
        elif self.first_name or self.last_name:
            return self.first_name or self.last_name
        else:
            return self.username

    def __str__(self):
        return f"{self.get_full_name} - {self.username}"

    def get_courses(self):
        Courses = apps.get_model('courses', 'CourseModel')
        filter = Courses.objects.filter(teacher=self)
        return filter

    def get_enrollments(self):
        Enrollments = apps.get_model('students', 'Enrollment')
        courses = self.get_courses()
        filter = Enrollments.objects.filter(course__in=courses, status=True, trial_lesson=False)
        return filter

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # first save the original

        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)
            # Fix rotation according to EXIF
            img = ImageOps.exif_transpose(img)
            # Example: Resize to max 300x300
            max_size = (800, 800)
            img.thumbnail(max_size)  # keeps aspect ratio
            img.save(img_path, format='JPEG', quality=85, optimize=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


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

    def __str__(self):
        return  f"{self.user.username} - {self.content_type.name} - {self.action_number}"

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'записи'


class TelegramChatsModel(models.Model):
    name = models.CharField(max_length=200)
    chat_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.chat_id}"