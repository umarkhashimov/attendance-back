from django.core.management.base import BaseCommand
from analytics.tasks import record_daily_analytics


class Command(BaseCommand):
 help = "test analytics"


 def handle(self, *args, **options):
    # noinspection PyBroadException
    try:
        record_daily_analytics()
        print('Success!')
    except Exception as e:
        print('Something went wrong...')
        print(e)
