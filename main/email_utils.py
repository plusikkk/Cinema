from django.core.mail import send_mail
from django.conf import settings

def send_email(order):
    tickets = order.tickets.all()
    recipient_email = order.user.email
    if not recipient_email:
        return False

    subject = f"Ваші квитки на фільм {tickets[0].session.movie.title}"
    message_lines = [
        f"Вітаємо, {order.user.username}!",
        "Дякуємо за ваше замовлення. Нижче прикріпляємо деталі ваших квитків:"
    ]
    for ticket in tickets:
        message_lines.append(f"Фільм: {ticket.session.movie.title}")
        message_lines.append(f"Кінотеатр: {ticket.session.hall.cinema.name}")
        message_lines.append(f"Початок сеансу: {ticket.session.start_time.strftime('%Y-%m-%d %H:%M')}")
        message_lines.append(f"Ряд {ticket.seat.row}, Місце {ticket.seat.num}")
        message_lines.append(f"Ціна: {ticket.price} UAH")

        full_message = "\n".join(message_lines)

        try:
            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,
                [recipient_email],
                fail_silently=False,
            )
            print(f"Квитки успішно надіслано на {recipient_email}")
            return True
        except Exception as e:
            print(f"Виникла помилка при надсиланні квитків: {e}")
            return False
