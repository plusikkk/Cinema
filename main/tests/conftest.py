import datetime
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from main.models import Genres, Movies, Actors, MovieBadges, Halls, Cinemas, CityBadges, CinemaBadges




@pytest.fixture(scope="function")
def api_client():
   return APIClient()




@pytest.fixture(scope="function")
def user() -> User:
   return User.objects.create_user(
       username='test_user',
       password='12345678',
       email='user@example.com',
   )




@pytest.fixture(scope="function")
def admin() -> User:
   return User.objects.create_superuser(
       username='admin',
       password='12345678',
       email='admin@example.com',
   )




@pytest.fixture(scope="function")
def genres():
   return Genres.objects.create(name='Test Genre')




@pytest.fixture(scope="function")
def actors():
   return Actors.objects.create(name='Test Actor')




@pytest.fixture(scope="function")
def badges() -> MovieBadges:
   return MovieBadges.objects.create(name='Test Badge')






@pytest.fixture
def movie(genres, actors, badges) -> Movies:
   movie = Movies.objects.create(
       id=1,
       title="New Movie",
       age_category="6",
       description="Test Movie description",
       trailer_url="https://example.com/trailer",
       poster_url="https://example.com/poster.jpg",
       rating=5,
       release_date=datetime.date(2025, 1, 1),
       end_date=datetime.date(2025, 12, 31),
       duration=120,
       director='Test Director'
   )




   movie.genres.add(genres)
   movie.actors.add(actors)
   movie.badges.add(badges)


   movie.save()


   return movie


@pytest.fixture(scope="function")
def movies_pagination():
   return [Movies.objects.create(title=f"Movie {i}",
                                 release_date=datetime.date(2025, 1, 1),
                                 duration=120
                                 ) for i in range(24)]


@pytest.fixture(scope="function")
def movie_random(db):
   def create_movie(**kwargs):
       defaults = {
           "title": "Test Movie",
           "release_date": datetime.date.today() - datetime.timedelta(days=10),
           "end_date": datetime.date.today() + datetime.timedelta(days=10),
           "age_category": 12,
           "duration": 120,
       }
       defaults.update(kwargs)
       return Movies.objects.create(**defaults)
   return create_movie






@pytest.fixture(scope="function")
def halls()-> Halls:
   halls =  Halls.objects.create(
        cinema_id = 1,
        name='Test Hall',
        number_of_seats=100
   )
   return halls


@pytest.fixture(scope="function")
def cinema(city,cinema_badge)->Cinemas:
   cinema = Cinemas.objects.create(
       id=1,
       name= 'Test Name',
       description = 'Test Description',
       address ='Test Address',
       photo="https://example.com/photo.jpg",
       latitude=50.45,
       longitude=30.52,
       city = city,
   )
   cinema.save()
   return cinema


@pytest.fixture
def city():
   city = CityBadges.objects.create(
       name="Kyiv"
   )
   return city


@pytest.fixture
def cinema_badge():
   cinema_badge = CinemaBadges.objects.create(
       name="IMAX",


   )
   return cinema_badge