from django.db import migrations


def create_and_update_seats(apps, schema_editor):
    # Отримання моделей
    Hall = apps.get_model('main', 'Halls')
    Seat = apps.get_model('main', 'Seats')

    ROWS = 6
    SEATS_PER_ROW = 12
    TOTAL_SEATS = ROWS * SEATS_PER_ROW

    all_halls = Hall.objects.all()
    seats_to_create = []

    for hall in all_halls:
        Seat.objects.filter(hall=hall).delete()

        for row_num in range(1, ROWS + 1):
            for seat_num in range(1, SEATS_PER_ROW + 1):
                seats_to_create.append(
                    Seat(
                        hall_id=hall.pk,
                        row=row_num,
                        num=seat_num
                    )
                )

        hall.number_of_seats = TOTAL_SEATS
        hall.save(update_fields=['number_of_seats'])

    Seat.objects.bulk_create(seats_to_create)


def reverse_seats(apps, schema_editor):
    Hall = apps.get_model('main', 'Halls')
    Seat = apps.get_model('main', 'Seats')

    Seat.objects.all().delete()
    Hall.objects.all().update(number_of_seats=0)


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_and_update_seats, reverse_code=reverse_seats),
    ]