import requests
from .models import Payment
from datetime import datetime
from django.conf import settings
import pytz


def subscribe(user):
    obj = Payment.objects.filter(user=user).first()
    if obj.ended_at < datetime.now(pytz.timezone(settings.TIME_ZONE)):
        return True
    return False


def verify(phone, code):
    headers = {
        "Authorization": settings.SMS_TOKEN}
    data = {
        'mobile_phone': phone,
        'message': f"Confirmation code from Edd Foot: {code}",
        'from': "Edd Foot",
        'callback_url': 'https://google.com/'
    }
    requests.post(url=settings.SMS_URL, data=data, headers=headers)
