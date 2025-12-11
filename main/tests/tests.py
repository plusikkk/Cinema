import pytest
from django.urls import reverse
from main.models import Movies

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
def test_post_movie_regular_user(api_client, user, badges,actors,genres,) -> None:
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
                                   "title": "New Movie",
                                   "age_category": 6,
                                   "description": "Test Movie description",
                                   "trailer_url": "https://example.com/trailer",
                                   "poster_url": "https://example.com/poster.jpg",
                                   "rating": 3,
                                   "release_date": "2025-01-01",
                                   "end_date": "2025-12-31",
                                   "duration": 120,
                                   "director": "Test Director",
                                   "genre_ids": [genres.id],
                                   "actor_ids": [actors.id],
                                   "badges":[badges.id],
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
                                    "title": "New Movie",
                                    "age_category": 6,
                                    "description": "Test Movie description",
                                    "trailer_url": "https://example.com/trailer",
                                    "poster_url": "https://example.com/poster.jpg",
                                    "rating": 3,
                                    "release_date": "2025-01-01",
                                    "end_date": "2025-12-31",
                                    "duration": 120,
                                    "director": "Test Director",
                                    "genre_ids": [genres.id],
                                    "actor_ids": [actors.id],
                                    "badges": [badges.id],
                                },format="json" )

    assert response.status_code == 403

@pytest.mark.django_db
def test_delete_movie_regular_user(api_client, user, badges, actors, genres, movie) -> None:
    api_client.force_authenticate(user=user)
    response = api_client.delete(reverse("movies-detail", args=[movie.id]),
                                {
                                    "title": "New Movie",
                                    "age_category": 6,
                                    "description": "Test Movie description",
                                    "trailer_url": "https://example.com/trailer",
                                    "poster_url": "https://example.com/poster.jpg",
                                    "rating": 3,
                                    "release_date": "2025-01-01",
                                    "end_date": "2025-12-31",
                                    "duration": 120,
                                    "director": "Test Director",
                                    "genre_ids": [genres.id],
                                    "actor_ids": [actors.id],
                                    "badges": [badges.id],
                                },format="json" )

    assert response.status_code == 403

@pytest.mark.django_db
def test_delete_movie_admin(api_client, admin, badges, actors, genres, movie) -> None:
    api_client.force_authenticate(user=admin)
    response = api_client.delete(reverse("movies-detail", args=[movie.id]),
                                {
                                    "title": "New Movie",
                                    "age_category": 6,
                                    "description": "Test Movie description",
                                    "trailer_url": "https://example.com/trailer",
                                    "poster_url": "https://example.com/poster.jpg",
                                    "rating": 3,
                                    "release_date": "2025-01-01",
                                    "end_date": "2025-12-31",
                                    "duration": 120,
                                    "director": "Test Director",
                                    "genre_ids": [genres.id],
                                    "actor_ids": [actors.id],
                                    "badges": [badges.id],
                                },format="json" )

    assert response.status_code == 204
    assert Movies.objects.filter(id=movie.id).exists() is False

@pytest.mark.django_db
def


















