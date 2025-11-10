from django.urls import path

from main import views

urlpatterns = [
    path('movies/', views.MovieList.as_view(), name='movies-list'),
    path('movies/<int:pk>/', views.MovieDetail.as_view(), name='movies-detail'),
    path('cinemas/', views.CinemaList.as_view(), name='cinemas-list'),
    path('cinemas/<int:pk>/', views.CinemaDetail.as_view(), name='cinemas-detail'),
]