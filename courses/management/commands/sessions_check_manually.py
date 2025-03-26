from django.core.management.base import BaseCommand
import datetime
from courses.tasks import mark_unmarked_sessions


class Command(BaseCommand):
 help = "Runs the APScheduler for Django"

 def add_arguments(self, parser):
    parser.add_argument("--date",
            type=str,
            help="Date in YYYY-MM-DD format",
            required=True)

 def handle(self, *args, **options):
    date_str = options["date"]
    # noinspection PyBroadException
    try:
        date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        if date:
            print(f'Checking sessions manually: {date}')
            mark_unmarked_sessions(date)
        else:
            print(f'Something went wrong...')
    except:
        print('Something went wrong...')
