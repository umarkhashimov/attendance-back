from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from .models import SessionsModel, CourseModel

@receiver(post_save, sender=CourseModel)
def create_sessions(sender, instance, created, **kwargs):
    if created:
        start_date = instance.start_date
        for i in range(instance.total_lessons):
            SessionsModel.objects.create(
                course=instance,
                session_number=i + 1,
                date=start_date + timedelta(weeks=i)  # Example: weekly sessions; adjust as needed
            )
