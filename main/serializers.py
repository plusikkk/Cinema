from rest_framework import serializers
from .models import Genres, Actors, Movies, Cinemas, Halls, Sessions, Seats, Tickets, Order


# Я не розписувала поля вручну де це не було необхідно\неважливо
# Також деякі поля не писала на свій розсуд
# Якщо будуть якісь проблеми або не згодні кажіть

class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = '__all__'

class ActorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actors
        fields = '__all__'

class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        fields = ['id', 'title', 'poster_url', 'rating', 'age_category']

class MoviesSerializer(serializers.ModelSerializer):
    genres = GenresSerializer(many=True, read_only=True)
    actors = ActorsSerializer(many=True, read_only=True)

    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Genres.objects.all(),
        source='genres',
        write_only=True
    )
    actor_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Actors.objects.all(),
        source='actors',
        write_only=True
    )

    class Meta:
        model = Movies
        fields = ['id', 'title', 'age_category', 'description', 'trailer_url',
                  'poster_url', 'rating', 'release_date', 'duration', 'director',
                  'genres', 'actors', 'genre_ids', 'actor_ids']

class HallsSerializer(serializers.ModelSerializer):
    cinema = serializers.StringRelatedField()

    class Meta:
        model = Halls
        fields = ['id', 'name', 'cinema']
        # не вказувала 'number_of_seats'

class CinemaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinemas
        fields = ['id', 'name']

class CinemasSerializer(serializers.ModelSerializer):
    halls = HallsSerializer(many=True, read_only=True)

    class Meta:
        model = Cinemas
        fields = ['id', 'name', 'description', 'address']
        # можна було б написати 'halls', але не думаю, що треба та координати

class SessionsSerializer(serializers.ModelSerializer):
    movie = MoviesSerializer(read_only=True)
    hall = HallsSerializer(read_only=True)

    class Meta:
        model = Sessions
        fields = ['id', 'movie', 'hall', 'start_time', 'end_time', 'price']
        # нема 'is_active'

class SeatsSerializer(serializers.ModelSerializer):
    hall = HallsSerializer(read_only=True)

    class Meta:
        model = Seats
        fields = ['id', 'num', 'row', 'hall']


class TicketsSerializer(serializers.ModelSerializer):
    seat = SeatsSerializer(read_only=True)
    session = SessionsSerializer(read_only=True)

    seat_id = serializers.PrimaryKeyRelatedField(queryset=Seats.objects.all(), source='seat', write_only=True)
    session_id = serializers.PrimaryKeyRelatedField(queryset=Sessions.objects.all(), source='session', write_only=True)

    class Meta:
        model = Tickets
        fields = ['id', 'price', 'session', 'seat', 'session_id', 'seat_id', 'is_cancelled']

    # Валідність на зайняття місця для сеансу та чи активний сам сеанс
    def validate(self, data):
        session = data.get('session')
        seat = data.get('seat')

        if not session.is_active:
            raise serializers.ValidationError("Квиток неможливо забронювати, бо сеанс неактивний")

        if Tickets.objects.filter(session=session, seat=seat, is_cancelled=False).exists():
            raise serializers.ValidationError("Це місце вже заброньовано для обраного сеансу")
        return data

class OrdersSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    tickets = TicketsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_amount', 'status', 'liqpay_order_id', 'tickets']

    # Одразу вписує юзера при покупці квитка
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)




