import json
from base64 import b64decode
from random import choice
from liqpay import LiqPay
from datetime import date

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
from main.models import Movies, Cinemas, Sessions, Seats, Order, Tickets, BonusTransaction, UserProfile
from main.serializers import MoviesSerializer, CinemasSerializer, CinemaListSerializer, SessionsSerializer, \
    UserSerializer, SeatsSerializer, MovieBadgesSerializer


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

        is_animation = request.query_params.get('animation')
        if is_animation == 'true':
            movies = movies.filter(
                Q(genres__name__icontains='Мульт') |
                Q(genres__name__icontains='мульт') |
                Q(genres__name__icontains='Анімац') |
                Q(genres__name__icontains='анімац')
            ).distinct()

        is_kids = request.query_params.get('kids')
        if is_kids == 'true':
            movies = movies.filter(
                Q(age_category__lte=12) &
                (   Q(genres__name__icontains='Мульт') |
                    Q(genres__name__icontains='мульт') |
                    Q(genres__name__icontains='Анімац') |
                    Q(genres__name__icontains='анімац')
                )
            ).distinct()

        age_limit = request.query_params.get('age_limit')
        if age_limit:
            try:
                limit_val = int(age_limit)
                movies = movies.filter(age_category__lt= limit_val)
            except ValueError:
                pass

        genres = request.query_params.get('genres')
        if genres:
            genre_list = genres.split(',')
            movies = movies.filter(genres__name__in=genre_list).distinct()

        search_query = request.query_params.get('search', None)
        if search_query:
            movies = movies.filter(
                Q(title__icontains=search_query) |
                Q(actors__name__icontains=search_query) |
                Q(director__icontains=search_query)
            ).distinct()

        movies = movies.order_by('-release_date')

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
                Q(genres__name__icontains='Мульт') |
                Q(genres__name__icontains='мульт') |
                Q(genres__name__icontains='Анімац') |
                Q(genres__name__icontains='анімац')
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
        use_bonuses = request.data.get('use_bonuses', False)

        if not session_id or not seat_id:
            return Response({"error": 'Потрібно вказати session_id and seat_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            session = Sessions.objects.get(id=session_id, is_active=True)

            # ПЕРЕВІРКА НА ВІК
            movie = session.movie
            user = request.user

            if movie.age_category >= 16:
                if not hasattr(user, 'profile') or not user.profile.birth_date: # Якщо що attr -> attribute
                    return Response({"error": f"Фільм має вікове обмеження {movie.age_category}+. Для купівлі квитка необхідно вказати дату народження в профілі."}, status=status.HTTP_403_FORBIDDEN)
                else:
                    birth_date = user.profile.birth_date
                    today = date.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

                    if age < movie.age_category:
                        return Response({"error": f"Фільм доступний для перегляду лише з {movie.age_category} років."}, status=status.HTTP_403_FORBIDDEN)

            seats = Seats.objects.filter(id__in=seat_id, hall=session.hall)

            if len(seats) != len(seat_id):
                return Response({"error": 'Обрані місця невірні'}, status=status.HTTP_400_BAD_REQUEST)

            original_amount = session.price * len(seats)
            amount_to_pay = original_amount
            bonuses_used = 0

            if use_bonuses:
                user_balance = request.user.profile.bonus_balance
                if user_balance > 0:
                    bonuses_used = min(user_balance, original_amount)
                    amount_to_pay = original_amount - bonuses_used

            order = Order.objects.create(
                user=request.user,
                total_amount=amount_to_pay,
                bonuses_used=bonuses_used,
                status=Order.OrderStatus.PENDING
            )

            if bonuses_used > 0:
                request.user.profile.bonus_balance -= bonuses_used
                request.user.profile.save()

                BonusTransaction.objects.create(
                    user=request.user,
                    amount=-bonuses_used,
                    transaction_type=BonusTransaction.TransactionType.REDEMPTION
                )

            tickets_create = []
            for seat in seats:
                tickets_create.append(Tickets(order=order, seat=seat, session=session, price=session.price))
            Tickets.objects.bulk_create(tickets_create)

            liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
            base_url = "https://overlate-unmorbidly-gwenda.ngrok-free.dev" #ЗАМІНИТИ ПРИ НАСТУПНОМУ ЗАПУСКУ

            if amount_to_pay == 0:
                order.status = Order.OrderStatus.PAID
                order.save()
                return Response({"status": "success", "message": "Paid by bonuses"}, status=status.HTTP_201_CREATED)

            params = {
                "action": "pay",
                "amount": str(amount_to_pay),
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
            confirm_payment(order.id)

            try:
                send_email(order)
            except Exception as e:
                print(f"Виникла помилка при надсиланні квитків: {e}")

        elif payment_status in ['error', 'failed', 'failure']:
            cancel_bonuses_payment(order.id)
            # подальша логіка (можливо видалення квитків які не пройшли оплату)
        return Response(status=status.HTTP_200_OK)

@transaction.atomic
def confirm_payment(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    if order.status == Order.OrderStatus.PAID:
        return

    order.status = Order.OrderStatus.PAID
    bonus_amount = int(order.total_amount * 0.03)
    order.bonuses_earned = bonus_amount
    order.save()

    if bonus_amount > 0:
        user = order.user
        user.profile.bonus_balance += bonus_amount
        user.profile.save()

        BonusTransaction.objects.create(user=user, amount=bonus_amount, transaction_type=BonusTransaction.TransactionType.ACCRUAL, order=order)

@transaction.atomic
def cancel_bonuses_payment(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    if order.status == Order.OrderStatus.FAILED:
        return

    order.status = Order.OrderStatus.FAILED
    order.save()

    if order.bonuses_used > 0:
        user = order.user
        user.profile.bonus_balance += order.bonuses_used
        user.profile.save()

        BonusTransaction.objects.create(user=user, amount=order.bonuses_used, transaction_type=BonusTransaction.TransactionType.REFUNDED, order=order)

    order.tickets.all().delete()
    print(f"Order canceled #{order.id}")
    
class UpdateUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        UserProfile.objects.get_or_create(user=request.user)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request):
        user = request.user
        user_id = user.id
        try:
            user.delete()
            return Response({"message": f"Користувача #{user_id} було успішно видалено"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": f"Помилка видалення"}, status=status.HTTP_400_BAD_REQUEST)

class SessionSeatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        try:
            session = Sessions.objects.get(id=session_id)
        except Sessions.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        seats = Seats.objects.filter(hall=session.hall).order_by('row', 'num')

        occupied_seat_ids = set(Tickets.objects.filter(
            session=session,
            order__status__in=[Order.OrderStatus.PAID, Order.OrderStatus.PENDING]
        ).values_list('seat_id', flat=True))

        serializer = SeatsSerializer(seats, many=True)
        seats_data = serializer.data

        for seat in seats_data:
            seat['is_occupied'] = seat['id'] in occupied_seat_ids
            seat['price'] = session.price

        badges_serializer = MovieBadgesSerializer(session.movie.badges.all(), many=True)

        return Response({
            "movie_title": session.movie.title,
            "cinema_name": session.hall.cinema.name,
            "hall_name": session.hall.name,
            "start_time": session.start_time,
            "seats": seats_data,
            "session_price": session.price,
            "poster_url": session.movie.poster_url,
            "badges": badges_serializer.data,
            "rating": session.movie.rating,
            "age_category": session.movie.age_category,
            "duration": session.movie.get_duration_display(),
        })




