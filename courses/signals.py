from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, datetime
from .models import SessionsModel, CourseModel

@receiver(post_save, sender=CourseModel)
def create_sessions(sender, instance, created, **kwargs):
    if created:
        lesson_days = [i for i in instance.weekdays]
        current_date = instance.start_date
        created_count = 0

        while created_count < instance.total_lessons:
            if str(current_date.weekday()) in lesson_days:
                SessionsModel.objects.create(course=instance, date=current_date, session_number=created_count + 1,)
                print('created session: ', current_date.strftime("%A, %B %d, %Y"), current_date.weekday())
                created_count += 1
            
            current_date += timedelta(days=1)

