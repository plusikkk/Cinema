from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ForeignKey
from django.db.models.fields import CharField, URLField, IntegerField
from django.conf import settings


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
    photo = URLField('Фото', max_length=300, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Актор'
        verbose_name_plural = 'Актори'
        ordering = ['name']

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
    trailer_url = models.URLField('Трейлер', max_length=300)
    poster_url = models.URLField('Постер', max_length=300)
    rating = models.PositiveSmallIntegerField('Рейтинг', default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    release_date = models.DateField('Дата релізу')
    end_date = models.DateField('Дата кінця показів', null=True, blank=True)
    duration = models.PositiveIntegerField('Тривалість (хвилини)',validators=[MinValueValidator(1), MaxValueValidator(500)])
    genres = models.ManyToManyField(Genres, verbose_name='Жанр', related_name='movies')
    director = models.CharField('Режисер', max_length=100)
    actors = models.ManyToManyField(Actors, verbose_name='Актори', related_name='movies')

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
    date_time = models.DateTimeField('Дата та час')
    movie = models.ForeignKey(Movies, on_delete=models.PROTECT, verbose_name='Фільм', related_name='sessions')
    price = models.IntegerField('Ціна', validators=[MinValueValidator(0), MaxValueValidator(500)])
    hall = ForeignKey(Halls, on_delete=models.PROTECT, verbose_name='Зала', related_name='sessions')
    is_active = models.BooleanField('Активний', default=True)  # для скасованих сеансів

    def __str__(self):
        return f"{self.movie.title} - {self.date_time.strftime('%d.%m.%Y %H:%M')}"

    def get_available_seats(self):
        booked = Tickets.objects.filter(session=self).count()
        return self.hall.number_of_seats - booked

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеанси'
        ordering = ['date_time']

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

class Tickets(models.Model):
    session = ForeignKey(Sessions, on_delete=models.PROTECT, verbose_name='Сеанс', related_name='tickets')
    seat = ForeignKey(Seats, on_delete=models.PROTECT, verbose_name='Місце', related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Клієнт', related_name='tickets')
    purchase_date_time = models.DateTimeField('Дата та час покупки', auto_now_add=True)
    price = models.IntegerField('Ціна квитка',help_text='Ціна на момент покупки', validators=[MinValueValidator(0), MaxValueValidator(500)])
    is_cancelled = models.BooleanField('Скасовано', default=False)

    # Для онлайн-оплати
    payment_status = models.CharField(
        'Статус оплати',
        max_length=20,
        choices=[
            ('pending', 'Очікується'),
            ('paid', 'Оплачено'),
            ('failed', 'Помилка'),
            ('refunded', 'Повернено'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"Квиток #{self.id} - {self.session.movie.title}"

    class Meta:
        verbose_name = 'Квиток'
        verbose_name_plural = 'Квитки'
        ordering = ['-purchase_date_time']
        unique_together = ['session', 'seat']








