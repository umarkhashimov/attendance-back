from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Max
from .models import StudentModel

@receiver(pre_save, sender=StudentModel)
def set_student_id(sender, instance, **kwargs):
    # Check if student_id is already set; if not, generate a new one
    if not instance.student_id:
        max_id = StudentModel.objects.aggregate(Max('student_id'))['student_id__max']
        instance.student_id = max_id + 1 if max_id and max_id >= 100000 else 100000
