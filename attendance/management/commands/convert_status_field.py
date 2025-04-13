import time
from django.core.management.base import BaseCommand
from attendance.models import AttendanceModel

class Command(BaseCommand):
    help = "Copy status field values to temp field"

    def handle(self, *args, **options):
        all = AttendanceModel.objects.all()
        for attendance in all:
            if attendance.status is True:
                attendance.status_ch = 1
            elif attendance.status is False:
                attendance.status_ch = 0
            else:
                attendance.status_ch = None

            attendance.save()
        self.stdout.write(self.style.SUCCESS("Copying fields values"))

