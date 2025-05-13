from django.core.management.base import BaseCommand
import datetime
from students.models import Enrollment


class Command(BaseCommand):
 help = "Copying dates"

 def handle(self, *args, **options):
    try:
        print('Copying dates...')
        enrollments = Enrollment.objects.all()
        for enrollment in enrollments:
           if enrollment.enrolled_at:
               enrollment.created_at = enrollment.enrolled_at
               enrollment.save()
        print('Done')
    except:
        print('Something went wrong...')
