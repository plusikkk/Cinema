import random
from django.conf import settings
from django.core.mail import send_mail
from Auth.models import AuthCode


def send_act_email(user, request):
    code = str(random.randint(100000, 999999))
    AuthCode.objects.update_or_create(user=user, defaults={'code': code})
    subject = "Підтвердіть вашу електронну адресу"
    message = f"""
    Вітаємо, {user.username}!
    
    Ваш код для підтвердження (нікому не повідомляйте код):
    {code}
    """

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False)
