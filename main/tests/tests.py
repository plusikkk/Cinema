import pytest
from django.urls import reverse
from main.models import Movies, Cinemas, Genres


@pytest.mark.django_db
def test_get_movie_list(api_client,movie) -> None:
   response = api_client.get(reverse('movies-list'), format ='json')
   assert response.status_code == 200
   assert len(response.data)== 4

@pytest.mark.django_db
def test_get_movie_empty_list(api_client) -> None:
   response = api_client.get(reverse('movies-list'), format='json')
   assert response.status_code == 200
   assert response.data['results'] == []
   assert response.data['count'] == 0

@pytest.mark.django_db
def test_post_movie_admin(api_client, admin, badges,actors,genres) -> None:
   api_client.force_authenticate(user=admin)
   response = api_client.post(reverse('movies-list'), {
                                  "title": "New Movie",
                                  "age_category": 6,
                                  "description": "Test Movie description",
                                  "trailer_url": "https://example.com/trailer",
                                  "poster_url": "https://example.com/poster.jpg",
                                  "rating": 5,
                                  "release_date": "2025-01-01",
                                  "end_date": "2025-12-31",
                                  "duration": 120,
                                  "director": "Test Director",
                                  "genre_ids": [genres.id],
                                  "actor_ids": [actors.id],
                                  "badges":[badges.id],
                              },format="json")
   assert response.status_code == 201
   assert Movies.objects.count() == 1
   assert Movies.objects.first().title == "New Movie"

@pytest.mark.django_db
def test_post_movie_regular_user(api_client, user, badges,actors,genres) -> None:
   api_client.force_authenticate(user=user)
   response = api_client.post(reverse('movies-list'),
                              {
                                  "title": "New Movie",
                                  "age_category": 6,
                                  "description": "Test Movie description",
                                  "trailer_url": "https://example.com/trailer",
                                  "poster_url": "https://example.com/poster.jpg",
                                  "rating": 5,
                                  "release_date": "2025-01-01",
                                  "end_date": "2025-12-31",
                                  "duration": 120,
                                  "director": "Test Director",
                                  "genres": [genres.id],
                                  "actors": [actors.id],
                                  "badges":[badges.id],
                              }, format="json")

   assert response.status_code == 403
   assert Movies.objects.count() == 0

@pytest.mark.django_db
def test_patch_movie_admin(api_client, admin, badges,actors,genres,movie) -> None:
   api_client.force_authenticate(user=admin)
   response = api_client.patch(reverse("movies-detail",args=[movie.id]),
                              {
                                  "rating": 3,
                              },
                              format="json"
                              )
   assert response.status_code == 200
   assert Movies.objects.first().rating == 3

@pytest.mark.django_db
def test_patch_movie_regular_user(api_client, user, badges, actors, genres, movie) -> None:
   api_client.force_authenticate(user=user)
   response = api_client.patch(reverse("movies-detail", args=[movie.id]),
                               {
                                   "rating": 3,
                               },format="json" )
   assert response.status_code == 403

@pytest.mark.django_db
def test_delete_movie_regular_user(api_client, user, badges, actors, genres, movie) -> None:
   api_client.force_authenticate(user=user)
   response = api_client.delete(reverse("movies-detail", args=[movie.id]),format="json" )
   assert response.status_code == 403

@pytest.mark.django_db
def test_delete_movie_admin(api_client, admin, badges, actors, genres, movie) -> None:
   api_client.force_authenticate(user=admin)
   response = api_client.delete(reverse("movies-detail", args=[movie.id]),format="json" )
   assert response.status_code == 204
   assert Movies.objects.filter(id=movie.id).exists() is False

@pytest.mark.django_db
def test_patch_non_existing_movie(api_client, admin,genres,actors,badges ) -> None:
   api_client.force_authenticate(user=admin)
   response = api_client.patch(reverse("movies-detail", args=[10]), format="json" )
   assert response.status_code == 404

@pytest.mark.django_db
def test_delete_non_existing_movie(api_client, admin,genres,actors,badges ) -> None:
   api_client.force_authenticate(user=admin)
   response = api_client.delete(reverse("movies-detail", args=[10]))
   assert response.status_code == 404

@pytest.mark.django_db
def test_get_movie_details(api_client, movie,genres,actors,badges) -> None:
   response = api_client.get(reverse("movies-detail", args=[movie.id]), format="json" )
   assert response.status_code == 200
   assert response.data["title"] == "New Movie"
   assert response.data["description"] == "Test Movie description"
   assert response.data["trailer_url"] == "https://example.com/trailer"
   assert response.data["poster_url"] == "https://example.com/poster.jpg"
   assert response.data["rating"] == 5
   assert response.data["release_date"] == "2025-01-01"
   assert response.data["duration"] == 120
   assert response.data["director"] == "Test Director"
   assert response.data["genres"] == [ {"id": genres.id, "name": genres.name}]
   assert response.data["actors"] == [ {"id": actors.id, "name": actors.name, "photo": actors.photo}]
   assert response.data["badges"] == [ {"id": badges.id, "name": badges.name,"description": badges.description,}]


# тести для пагінації
@pytest.mark.django_db
def test_max_page_size_limit_movie_pagination(api_client,movies_pagination):
   response = api_client.get(reverse("movies-list") + "?page_size=100", format="json")
   assert response.status_code == 200
   assert len(response.data["results"]) == 24

@pytest.mark.django_db
def test_second_page_movie_pagination(api_client,movies_pagination):
    response = api_client.get(reverse("movies-list") + "?page=2")
    assert response.status_code == 200
    assert "results" in response.data

@pytest.mark.django_db
def test_default_movie_pagination(api_client,movies_pagination):
   response = api_client.get(reverse("movies-list"),format="json")
   assert response.status_code == 200
   assert len(response.data["results"])== 4

#тести для рандомайзеру
@pytest.mark.django_db
def test_random_movie_success(api_client, movie_random):
    movie_random(title="Movie 1")
    movie_random(title="Movie 2")
    response = api_client.post(reverse("random-movie"), {}, format="json")
    assert response.status_code == 200
    assert "title" in response.data

@pytest.mark.django_db
def test_random_movie_animation_filter(api_client, movie_random,genres,movie,):
    genre = Genres.objects.create(name="animation")
    movie = movie_random(title="Animation Movie")
    movie.genres.add(genre)
    response = api_client.post(reverse("random-movie"),{
        "type": "animation"
    }, format="json")
    assert response.status_code == 200
    assert response.data["title"] == "Animation Movie"

@pytest.mark.django_db
def test_random_movie_family_filter(api_client, movie_random):
    movie_random(title="Family Movie", age_category=6)
    movie_random(title="Adult Movie", age_category=18)
    response = api_client.post(reverse("random-movie"),{
        "family": "family"
    },format="json")
    assert response.status_code == 200
    assert response.data["age_category"] < 16

@pytest.mark.django_db
def test_random_movie_rating_filter(api_client, movie_random):
    movie_random(title="Teen Movie", age_category=16)
    movie_random(title="18+ Movie", age_category=18)
    response = api_client.post( reverse("random-movie"),
        {"rating": "18+"
         }, format="json"
    )
    assert response.status_code == 200
    assert response.data["age_category"] < 18

@pytest.mark.django_db
def test_random_movie_no_results(api_client):
    response = api_client.post(
        reverse("random-movie"), {
            "type": "animation"
        },format="json")
    assert response.status_code == 204

@pytest.mark.django_db
def test_random_movie_allow_any(api_client, movie_random):
    movie_random(title="Public Movie")
    response = api_client.post(reverse("random-movie"), {}, format="json")
    assert response.status_code == 200

#тести для кіотеатрів
@pytest.mark.django_db
def test_get_cinema_list(api_client,cinema,city)-> None:
   response = api_client.get(reverse('cinemas-list'), format='json')
   assert response.status_code == 200

@pytest.mark.django_db
def test_get_cinema_empty_list(api_client) -> None:
   response = api_client.get(reverse('cinemas-list'), format='json')
   assert response.status_code == 200
   assert response.data == []
   assert len(response.data) == 0

@pytest.mark.django_db
def test_get_cinema_detail(api_client, cinema,city,cinema_badge):
    response = api_client.get(
        reverse("cinemas-detail", args=[cinema.id])
    )
    assert response.status_code == 200
    assert response.data["name"] =='Test Name'
    assert response.data["address"] == 'Test Address'
    assert response.data["description"] == 'Test Description'
    assert response.data["city"] == {"id": 1, "name": city.name}
    assert response.data["badges"][0]["name"] == cinema_badge.name
    assert response.data["photo"] == "https://example.com/photo.jpg"
    assert response.data["latitude"] == '50.450000'
    assert response.data["longitude"] == '30.520000'

@pytest.mark.django_db
def test_post_cinema_admin(api_client, admin, city,cinema_badge) -> None:
    api_client.force_authenticate(user=admin)
    response = api_client.post(
        reverse("cinemas-list"),
        {
            "name": "New Cinema",
            "description": "Cinema description",
            "address": "Cinema address",
            "photo": "https://example.com/photo.jpg",
            "latitude": '50.450000',
            "longitude": '30.520000',
            "city_id": city.id,
            "badges": [cinema_badge.id],
        },
        format="json"
    )
    assert response.status_code == 201
    assert Cinemas.objects.count() == 1
    assert Cinemas.objects.first().name == "New Cinema"

@pytest.mark.django_db
def test_patch_cinema_admin(api_client,cinema,admin) -> None:
   api_client.force_authenticate(user=admin)
   response = api_client.patch(reverse("cinemas-detail",args=[cinema.id]),
                              {
                                    "name":"cinema 2",
                              },
                              format="json"
                              )
   assert response.status_code == 200
   assert Cinemas.objects.first().name == "cinema 2"

@pytest.mark.django_db
def test_patch_cinema_regular_user(api_client, user, cinema) -> None:
   api_client.force_authenticate(user=user)
   response = api_client.patch(reverse("cinemas-detail", args=[cinema.id]),
                               {
                                   "name":"cinema 2",
                               },format="json" )
   assert response.status_code == 403

@pytest.mark.django_db
def test_delete_cinema_regular_user(api_client, cinema,city,cinema_badge,user) -> None:
   api_client.force_authenticate(user=user)
   response = api_client.delete(reverse("cinemas-detail", args=[cinema.id]),format="json" )
   assert response.status_code == 403




