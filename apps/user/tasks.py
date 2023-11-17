from celery import shared_task
from .models import Notification


@shared_task(bind=True)
def send_notification_task(*args, **kwargs):
    text_en = kwargs.get('text_en')
    text_uz = kwargs.get('text_uz')
    text_ru = kwargs.get('text_ru')
    students = kwargs.get('students')
    for i in students:
        Notification.objects.create(user_id=i, text_en=text_en, text_ru=text_ru, text_uz=text_uz)
    return "Sent"
