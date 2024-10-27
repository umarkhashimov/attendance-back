from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import UsersModel

# @receiver(post_save, sender=UsersModel)
# def create_user(sender, instance, created, **kwargs):
#     if created:
#         pswd = instance.password
#         user = UsersModel.objects.get(id=instance.id)
#         user.set_password(pswd)
#         user.save()