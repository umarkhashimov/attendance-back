from django.core.management.base import BaseCommand
from students.models import StudentModel, Enrollment


class Command(BaseCommand):
 help = "Archive inactive students"


 def handle(self, *args, **options):
    # noinspection PyBroadException
    print('Archiving inactive students')

    try:
        students = StudentModel.objects.all()
        for student in students:
            active_enrollments = Enrollment.objects.filter(student=student, status=True).count()
            if active_enrollments < 1:
                student.archived = True
                student.save()
        print('Done!')
    except:
        print('Something went wrong...')
