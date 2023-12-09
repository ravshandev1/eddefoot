from celery import shared_task
from .models import Notification, User
from pyfcm import FCMNotification
from django.conf import settings


@shared_task(bind=True)
def send_notification_task(*args, **kwargs):
    push_service = FCMNotification(api_key=settings.FIREBASE_KEY)
    text_en = kwargs.get('text_en')
    text_uz = kwargs.get('text_uz')
    text_ru = kwargs.get('text_ru')
    students = kwargs.get('students')
    for i in students:
        Notification.objects.create(user_id=i, text_en=text_en, text_ru=text_ru, text_uz=text_uz)
        user = User.objects.filter(id=i).first()
        push_service.notify_single_device(registration_id=user.firebase_token, message_title=text_en,
                                          message_body=text_en,
                                          message_icon=open(f'{settings.STATIC_ROOT}/logo.svg', 'rb'))
    return "Sent"
