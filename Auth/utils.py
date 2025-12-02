from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail


def send_act_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = "127.0.0.1:8000"
    activation_link = f"http://{domain}/activation/{uid}/{token}/"
    subject = "Підтвердіть вашу електронну адресу"
    message = f"""
    Вітаємо, {user.username}!
    
    Для того щоб підтвердити електронну адресу натисніть на посилання нижче:
    {activation_link}
    """

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False)
