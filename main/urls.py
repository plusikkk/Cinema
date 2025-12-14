from django.urls import include, path
from main import views
from main.views import SessionSeatsView

urlpatterns = [
    path('movies/', views.MovieList.as_view(), name='movies-list'),
    path('movies/<int:pk>/', views.MovieDetail.as_view(), name='movies-detail'),
    path('cinemas/', views.CinemaList.as_view(), name='cinemas-list'),
    path('cinemas/<int:pk>/', views.CinemaDetail.as_view(), name='cinemas-detail'),
    path('sessions/', views.SessionList.as_view(), name='sessions-list'),
    path('orders/create/', views.CreateOrder.as_view(), name='create-order'),
    path('payment/callback/', views.LiqPayCallback.as_view(), name='payment-callback'),
    path('random-movie/', views.RandomMovie.as_view(), name='random-movie'),
    path('auth/userprofile/', views.UpdateUser.as_view(), name='userprofile-detail'),
    path('sessions/<int:session_id>/seats/', SessionSeatsView.as_view(), name='session_seats'),
]
