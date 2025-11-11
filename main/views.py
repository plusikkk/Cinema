from random import random

from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q
from django.utils import timezone
from django.http import Http404

from main.models import Movies, Cinemas
from main.serializers import MoviesSerializer, MovieListSerializer, CinemasSerializer, CinemaListSerializer


class MovieList(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    #filters
    def get(self, request, format=None):
        movies = Movies.objects.all()
        today = timezone.now().date()

        status = request.query_params.get('status')
        if status == 'screened':
            movies = movies.filter(
                Q(release_date__lte=today),
                Q(end_date__gte=today) | Q(end_date__isnull=True)
            )
        elif status == 'soon':
            movies = movies.filter(release_date__gt=today)

        genres = request.query_params.get('genres')     # Фільтрація лінку
        if genres:
            movies = movies.filter(genres__name__icontains=genres).distinct()
        age_category = request.query_params.get('age_category')
        if age_category:
            movies = movies.filter(age_category__exact=age_category)
        actors = request.query_params.get('actors')
        if actors:
            movies = movies.filter(actors__name__icontains=actors).distinct()
        director = request.query_params.get('director')
        if director:
            movies = movies.filter(director__icontains=director)

        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = MoviesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # РАНДОМАЙЗЕР
class RandomMovie(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        movies = Movies.objects.all()

        # чекбокси
        movie_type = request.data.get('type')
        rating = request.data.get('rating')
        family = request.data.get('family')

        if movie_type == 'animation': # Мультфільми
            movies = movies.filter(genres__name__icontains='animation')

        if family == 'family': # Сімейні фільми до 16+
            movies = movies.filter(age_category__lt=16)

        if family == '18+': # Фільми до 18+
            movies = movies.filter(age_category__lt=18)

        today = timezone.now().date() # лише актуальні фільми
        movies = movies.filter(
            Q(release_date__lte=today),
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        ).distinct()

        movies_list = list(movies)
        if not movies_list:
            return Response({"Немає фільмів, що відповідають фільтрам"}, status=status.HTTP_204_NO_CONTENT)

        movie = random.choice(movies_list)
        serializer = MovieListSerializer(movie)
        return Response(serializer.data, status=200)



class MovieDetail(APIView):
    def get_permissions(self):
        if self.request.method != 'GET':
            return [IsAdminUser()]
        return [AllowAny()]

    def get_object(self, pk):
        try:
            return Movies.objects.get(pk=pk)
        except Movies.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        movie = self.get_object(pk)
        serializer = MoviesSerializer(movie)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        movie = self.get_object(pk)
        serializer = MoviesSerializer(movie, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        movie = self.get_object(pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






class CinemaList(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, format=None):
        cinemas = Cinemas.objects.all()
        serializer = CinemaListSerializer(cinemas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CinemasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CinemaDetail(APIView):
    def get_permissions(self):
        if self.request.method != 'GET':
            return [IsAdminUser()]
        return [AllowAny()]

    def get_object(self, pk):
        try:
            return Cinemas.objects.get(pk=pk)
        except Cinemas.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        cinema = self.get_object(pk)
        serializer = CinemasSerializer(cinema)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        cinema = self.get_object(pk)
        serializer = CinemasSerializer(cinema, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        cinema = self.get_object(pk)
        cinema.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



