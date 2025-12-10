import json
from base64 import b64decode
from random import choice
from liqpay import LiqPay

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.http import Http404

from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination


from main.email_utils import send_email
from main.models import Movies, Cinemas, Sessions, Seats, Order, Tickets
from main.serializers import MoviesSerializer, CinemasSerializer, CinemaListSerializer, SessionsSerializer


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

        search_query = request.query_params.get('search', None)
        if search_query:
            movies = movies.filter(
                Q(title__icontains=search_query) |
                Q(actors__name__icontains=search_query) |
                Q(director__icontains=search_query)
            ).distinct()

        paginator = MoviesPagination()
        paginated_movies = paginator.paginate_queryset(movies, request, view=self)
        serializer = MoviesSerializer(paginated_movies, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = MoviesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ПАГІНАЦІЯ
class MoviesPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 24



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
            movies = movies.filter(
                Q(genres__name__icontains='мультфільм') |
                Q(genres__name__icontains='анімація') |
                Q(genres__name__icontains='animation')
            )

        if family == 'family': # Сімейні фільми до 16+
            movies = movies.filter(age_category__lt=16)

        if rating == '18+': # Фільми до 18+
            movies = movies.filter(age_category__lt=18)

        today = timezone.now().date() # лише актуальні фільми
        movies = movies.filter(
            Q(release_date__lte=today),
            Q(end_date__gte=today) | Q(end_date__isnull=True)
        ).distinct()

        movies_list = list(movies)
        if not movies_list:
            return Response({"Немає фільмів, що відповідають фільтрам"}, status=status.HTTP_204_NO_CONTENT)

        movie = choice(movies_list)
        serializer = MoviesSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class SessionList(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        queryset = Sessions.objects.filter(is_active=True, start_time__gte=timezone.now())

        movie_id = request.query_params.get('movie')
        if movie_id is not None:
            queryset = queryset.filter(movie__id=movie_id)

        cinema_id = request.query_params.get('cinema')
        if cinema_id is not None:
            queryset = queryset.filter(hall__cinema_id=cinema_id)

        queryset = queryset.order_by('start_time')
        serializer = SessionsSerializer(queryset, many=True)
        return Response(serializer.data)

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

class CreateOrder(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, format=None):
        session_id = request.data.get('session_id')
        seat_id = request.data.get('seat_id')

        if not session_id or not seat_id:
            return Response({"error": 'Потрібно вказати session_id and seat_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            session = Sessions.objects.get(id=session_id, is_active=True)
            seats = Seats.objects.filter(id__in=seat_id, hall=session.hall)

            if len(seats) != len(seat_id):
                return Response({"error": 'Обрані місця невірні'}, status=status.HTTP_400_BAD_REQUEST)

            total_amount = session.price * len(seats)
            order = Order.objects.create(user=request.user, total_amount=total_amount, status=Order.OrderStatus.PENDING)
            tickets_create = []
            for seat in seats:
                tickets_create.append(Tickets(order=order, seat=seat, session=session, price=session.price))
            Tickets.objects.bulk_create(tickets_create)

            liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
            base_url = "https://overlate-unmorbidly-gwenda.ngrok-free.dev" #ЗАМІНИТИ ПРИ НАСТУПНОМУ ЗАПУСКУ

            params = {
                "action": "pay",
                "amount": str(total_amount),
                "currency": "UAH",
                "description": f"Tickets for {session.movie.title} (order #{order.id})",
                "order_id": str(order.liqpay_order_id),
                "version": "3",
                "sandbox": "1",
                "result_url": f"{base_url}/movies/{session.movie.id}/",
                "server_url": f"{base_url}/api/payment/callback/",
            }

            data = liqpay.cnb_data(params)
            signature = liqpay.cnb_signature(params)
            return Response({'data': data, 'signature': signature}, status=status.HTTP_201_CREATED)

        except Sessions.DoesNotExist:
            return Response({'error': 'Сеанс не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Внутрішня помилка: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiqPayCallback(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        data = request.data.get('data')
        signature = request.data.get('signature')

        if not data or not signature:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        expected_signature = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)

        if expected_signature != signature:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_data = json.loads(b64decode(data).decode('utf-8'))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        payment_status = decoded_data.get('status')
        liqpay_order_id = decoded_data.get('order_id')

        try:
            order = Order.objects.get(liqpay_order_id=liqpay_order_id)
        except Order.DoesNotExist:
            print(f"ПОМИЛКА: Отримано callback для неіснуючого liqpay_order_id: {liqpay_order_id}")
            return Response(status=status.HTTP_200_OK) #щоб не отримувати повторних запитів від лікпею

        if payment_status in ['success', 'sandbox']:
            order.status = Order.OrderStatus.PAID
            order.save()

            try:
                send_email(order)
            except Exception as e:
                print(f"Виникла помилка при надсиланні квитків: {e}")

        elif payment_status in ['error', 'failed', 'failure']:
            order.status = Order.OrderStatus.FAILED
            order.save()
            # подальша логіка (можливо видалення квитків які не пройшли оплату)
        return Response(status=status.HTTP_200_OK)





