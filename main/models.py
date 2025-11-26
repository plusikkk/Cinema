import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ForeignKey
from django.db.models.fields import CharField, URLField, IntegerField
from django.conf import settings
from django.utils import timezone


class Genres(models.Model):
    name = models.CharField('Назва', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'
        ordering = ['name']

class Actors(models.Model):
    name = CharField('Імʼя', max_length=100)
    photo = URLField('Фото', max_length=1000, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Актор'
        verbose_name_plural = 'Актори'
        ordering = ['name']

    # ЗНАЧОК ДО ФІЛЬМІВ З ДОП ІНФОЮ ПРО ЗНИЖКИ ПОКАЗИ І ТД
class MovieBadges(models.Model):
    name = models.CharField('Текст значка', max_length=100, help_text='Новинка, IMAX, Спецпоказ')
    description = models.CharField('Опис значка', max_length=225)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Значок фільму'
        verbose_name_plural = 'Значки фільму'

    # ЗНАЧОК ДО КІНОТЕАТРІВ З МІСТАМИ
class CityBadges(models.Model):
    name = models.CharField('Місто', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Місто'
        verbose_name_plural = 'Міста'

    # ЗНАЧОК ДО КІНОТЕАТРІВ З ДОП ІНФОЮ ПРО ЗРУЧНОСТІ ПОСЛУГИ І ТД
class CinemaBadges(models.Model):
    name = models.CharField('Текст значка', max_length=100, help_text='Parking, IMAX, LUX')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Значок кінотеатру'
        verbose_name_plural = 'Значки кінотеатру'


class Movies(models.Model):
    title = models.CharField('Назва фільму', max_length=200)
    age_category = models.PositiveSmallIntegerField('Вікова категорія',
        choices=[
            (0, 'Для всіх'),
            (6, '6+'),
            (12, '12+'),
            (16, '16+'),
            (18, '18+'),
        ],
        default=0
    )
    description = models.TextField('Опис')
    trailer_url = models.URLField('Трейлер', max_length=1000)
    poster_url = models.URLField('Постер', max_length=1000)
    rating = models.PositiveSmallIntegerField('Рейтинг', default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    release_date = models.DateField('Дата релізу')
    end_date = models.DateField('Дата кінця показів', null=True, blank=True)
    duration = models.PositiveIntegerField('Тривалість (хвилини)',validators=[MinValueValidator(1), MaxValueValidator(500)])
    genres = models.ManyToManyField(Genres, verbose_name='Жанр', related_name='movies')
    director = models.CharField('Режисер', max_length=100)
    actors = models.ManyToManyField(Actors, verbose_name='Актори', related_name='movies')
    badges = models.ManyToManyField(MovieBadges, verbose_name='Значок/Статус фільму')

    def __str__(self):
        return self.title

    def get_duration_display(self):
        #Повертає тривалість у форматі '...г ...хв
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0:
            return f"{hours}г {minutes}хв"
        return f"{minutes}хв"

    class Meta:
        verbose_name = 'Фільм'
        verbose_name_plural = 'Фільми'
        ordering = ['-release_date']

class Cinemas(models.Model):
    name = models.CharField('Назва', max_length=100)
    description = models.TextField('Опис')
    address = models.CharField('Адреса', max_length=250)
    photo = URLField('Фото', max_length=1000, blank=True)
    badges = models.ManyToManyField(CinemaBadges, verbose_name='Значок/Статус кінотеатру')
    city = models.ForeignKey(CityBadges, on_delete=models.PROTECT, verbose_name='Місто')


    #Для інтеграції апі гугл карт
    latitude = models.DecimalField(
        'Широта',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.DecimalField(
        'Довгота',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    def __str__(self):
        return self.name

    def get_map_url(self):
        #Посилання на Google Maps
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
        return None

    def get_coordinates(self):
        #Повертає координати як словник
        if self.latitude and self.longitude:
            return {
                'lat': float(self.latitude),
                'lng': float(self.longitude)
            }
        return None

    class Meta:
        verbose_name = 'Кінотеатр'
        verbose_name_plural = 'Кінотеатри'
        ordering = ['name']

class Halls(models.Model):
    name = models.CharField('Назва зали', max_length=50, default='Зала 1')
    number_of_seats = IntegerField('Кількість місць', validators=[MinValueValidator(0), MaxValueValidator(300)])
    cinema = models.ForeignKey(Cinemas, on_delete=models.CASCADE, verbose_name='Кінотеатр', related_name='halls')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Зала'
        verbose_name_plural = 'Зали'
        ordering = ['cinema', 'name']
        unique_together = ['cinema', 'name']

class Sessions(models.Model):
    start_time = models.DateTimeField('Дата та час початку', default=timezone.now)
    end_time = models.DateTimeField('Дата та час кінця', default=timezone.now)
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE, verbose_name='Фільм', related_name='sessions')
    price = models.IntegerField('Ціна', validators=[MinValueValidator(0)])
    hall = ForeignKey(Halls, on_delete=models.PROTECT, verbose_name='Зала', related_name='sessions')
    is_active = models.BooleanField('Активний', default=True)  # для скасованих сеансів

    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"

    def get_available_seats(self):
        booked = Tickets.objects.filter(session=self).count()
        return self.hall.number_of_seats - booked

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеанси'
        ordering = ['start_time']

class Seats(models.Model):
    hall = ForeignKey(Halls, on_delete=models.CASCADE, verbose_name='Зала', related_name='seats')
    num = IntegerField('Номер місця', validators=[MinValueValidator(0), MaxValueValidator(50)])
    row = IntegerField('Номер ряду' ,validators=[MinValueValidator(0), MaxValueValidator(6)])

    def __str__(self):
        return f"Ряд {self.row}, Місце {self.num}"

    def is_booked_for_session(self, session):
        #Перевірка чи зайнято місце для конкретного сеансу
        return Tickets.objects.filter(session=session, seat=self).exists()

    class Meta:
        verbose_name = 'Місце'
        verbose_name_plural = 'Місця'
        ordering = ['hall', 'row', 'num']
        unique_together = ['hall', 'row', 'num']

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Клієнт', related_name='orders')
    created_at = models.DateTimeField('Дата та час створення', auto_now_add=True)
    total_amount = models.IntegerField('Загальна сума', validators=[MinValueValidator(0)])
    status = models.CharField('Статус оплати', max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    liqpay_order_id = models.CharField('ID замовлення (LiqPay)', max_length=255, unique=True, db_index=True, default=uuid.uuid4)

    def __str__(self):
        return f"Замовлення #{self.id} від {self.user.username} ({self.get_status_display()})"

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

class Tickets(models.Model):
    session = ForeignKey(Sessions, on_delete=models.PROTECT, verbose_name='Сеанс', related_name='tickets')
    seat = ForeignKey(Seats, on_delete=models.PROTECT, verbose_name='Місце', related_name='tickets')
    price = models.IntegerField('Ціна квитка',help_text='Ціна на момент покупки', validators=[MinValueValidator(0), MaxValueValidator(500)])
    is_cancelled = models.BooleanField('Скасовано', default=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Замовлення', related_name='tickets')

    def __str__(self):
        return f"Квиток #{self.id} (Замовлення #{self.order.id}) - {self.session.movie.title}"

    class Meta:
        verbose_name = 'Квиток'
        verbose_name_plural = 'Квитки'
        ordering = ['-order__created_at']
        unique_together = ['session', 'seat']









