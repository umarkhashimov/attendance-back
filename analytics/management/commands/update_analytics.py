from django.core.management.base import BaseCommand
from analytics.tasks import record_daily_analytics
import datetime

class Command(BaseCommand):
    help = "test analytics"

    def add_arguments(self, parser):
        parser.add_argument("--date",
                            type=str,
                            help="Date in YYYY-MM-DD format",
                            required=False)

    def handle(self, *args, **options):
        # noinspection PyBroadException
        date_str = options["date"]

        try:
            if date_str:
                date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
                print(f'Checking sessions manually: {date}')
                record_daily_analytics(date)
            else:
                record_daily_analytics()

            print('Success!')
        except Exception as e:
            print('Something went wrong...')
            print(e)
