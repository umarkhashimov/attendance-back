import time
from django.core.management.base import BaseCommand

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from courses.tasks import mark_unmarked_sessions
from analytics.tasks import record_daily_analytics


class Command(BaseCommand):
 help = "Runs the APScheduler for Django"

 def handle(self, *args, **options):
     scheduler = BackgroundScheduler()
     scheduler.add_job(mark_unmarked_sessions, CronTrigger(hour=23, minute=00))  # 11 PM
     scheduler.add_job(mark_unmarked_sessions, CronTrigger(hour=23, minute=30))  # 11:30 PM
     scheduler.add_job(mark_unmarked_sessions, CronTrigger(hour=23, minute=40))  # 11:30 PM
     # scheduler.add_job(send_test_message, IntervalTrigger(hours=1), max_instances=1)  # every 1 hour
     scheduler.start()

     self.stdout.write(self.style.SUCCESS("APScheduler started..."))

     try:
         while True:  # Keep the process alive
             time.sleep(10)
     except (KeyboardInterrupt, SystemExit):
         self.stdout.write(self.style.WARNING("Stopping scheduler..."))
         scheduler.shutdown()