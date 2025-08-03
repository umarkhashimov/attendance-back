from django.core.management.base import BaseCommand
import datetime
import requests
from users.models import TelegramChatsModel
from decouple import config

from courses.tasks import mark_unmarked_sessions


def send_test_message():
    chats = TelegramChatsModel.objects.all().values_list('chat_id', flat=True)

    url = f"https://api.telegram.org/bot{config('ADMIN_BOT_TOKEN')}/sendMessage"

    for chat_id in chats:
        data = {"chat_id": chat_id, 'text': f"Тест..."}
        requests.post(url=url, data=data)

class Command(BaseCommand):
 help = "Send test message to TG chats"


 def handle(self, *args, **options):
    # noinspection PyBroadException
    try:
        send_test_message()
    except:
        print('Something went wrong...')
