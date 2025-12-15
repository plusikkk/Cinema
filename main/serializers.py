from random import choices

from rest_framework import serializers
from .models import Genres, Actors, Movies, Cinemas, Halls, Sessions, Seats, Tickets, Order, MovieBadges, CinemaBadges, \
    CityBadges, UserProfile
from  django.contrib.auth import get_user_model

User = get_user_model()

class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = '__all__'

class ActorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actors
        fields = '__all__'

    # ЗНАЧКИ
class MovieBadgesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieBadges
        fields = ['id', 'name', 'description']

class CityBadgesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityBadges
        fields = '__all__'

class CinemaBadgesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemaBadges
        fields = ['id', 'name',]

class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        fields = ['id', 'title', 'poster_url', 'rating', 'age_category', 'description', 'trailer_url']

class MoviesSerializer(serializers.ModelSerializer):
    genres = GenresSerializer(many=True, read_only=True)
    actors = ActorsSerializer(many=True, read_only=True)
    badges = MovieBadgesSerializer(many=True, read_only=True)

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
        fields = ['id', 'title', 'badges', 'age_category', 'description', 'trailer_url',
                  'poster_url', 'rating', 'release_date', 'duration', 'director',
                  'genres', 'actors', 'genre_ids', 'actor_ids', 'end_date']

class CinemaInHallSerializer(serializers.ModelSerializer):
    badges = CinemaBadgesSerializer(many=True, read_only=True)

    class Meta:
        model = Cinemas
        fields = ['id', 'name', 'badges']

class HallsSerializer(serializers.ModelSerializer):
    cinema = CinemaInHallSerializer(read_only=True)

    class Meta:
        model = Halls
        fields = ['id', 'name', 'cinema']
        # не вказувала 'number_of_seats'

class CinemaListSerializer(serializers.ModelSerializer):
    badges = CinemaBadgesSerializer(many=True, read_only=True)
    city = CityBadgesSerializer(read_only=True)

    class Meta:
        model = Cinemas
        fields = ['id', 'name', 'latitude', 'longitude', 'address', 'description', 'photo', 'badges', 'city']

class CinemasSerializer(serializers.ModelSerializer):
    halls = HallsSerializer(many=True, read_only=True)
    badges = CinemaBadgesSerializer(many=True, read_only=True)
    city = CityBadgesSerializer(read_only=True)

    class Meta:
        model = Cinemas
        fields = ['id', 'name', 'description', 'address', 'latitude', 'longitude', 'halls', 'badges', 'photo', 'city']

    def get_coordinates(self, obj):
        return obj.get_coordinates()

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
        fields = ['id', 'user', 'created_at', 'total_amount', 'status', 'liqpay_order_id', 'tickets', 'bonuses_used', 'bonuses_earned']

    # Одразу вписує юзера при покупці квитка
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False, allow_null=True, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ['birth_date', 'gender', 'bonus_balance']
        read_only_fields = ['bonus_balance']

    def validate_gender(self, value):
        if value == "":
            return None
        return value

    def validate_birth_date(self, value):
        if value is None or value == "":
            return None
        return value

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile', 'first_name', 'last_name']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        instance = super().update(instance, validated_data)

        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


