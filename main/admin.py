from django.contrib import admin
from .models import (
    Genres, Actors, Movies, Cinemas,
    Halls, Sessions, Seats, Tickets, MovieBadges
)

class HallInline(admin.TabularInline):
    model = Halls
    extra = 1
    ordering = ('name',)


class SeatInline(admin.TabularInline):
    model = Seats
    extra = 0
    readonly_fields = ('row', 'num')
    can_delete = False
    ordering = ('row', 'num')

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(MovieBadges)
class MovieBadgesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Movies)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_badges', 'release_date', 'age_category', 'rating', 'director')
    list_filter = ('badges', 'age_category', 'genres', 'release_date')
    search_fields = ('title', 'director')
    filter_horizontal = ('genres', 'actors', 'badges')

    def get_badges(self, obj):
        return ', '.join([b.name for b in obj.badges.all()])
    get_badges.short_description = 'Значки/Статуси'

@admin.register(Cinemas)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')
    inlines = [HallInline]

@admin.register(Halls)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'cinema', 'number_of_seats')
    list_filter = ('cinema',)
    search_fields = ('name', 'cinema__name')
    inlines = [SeatInline]

@admin.register(Sessions)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'movie', 'hall', 'date_time', 'price', 'is_active')
    list_filter = ('date_time', 'hall__cinema', 'movie', 'is_active')
    search_fields = ('movie__title', 'hall__name')
    autocomplete_fields = ['movie', 'hall']


@admin.register(Seats)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'hall')
    list_filter = ('hall__cinema', 'hall')
    search_fields = ('hall__name', 'hall__cinema__name', 'row', 'num')
    autocomplete_fields = ['hall']


@admin.register(Tickets)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'user', 'seat', 'purchase_date_time', 'payment_status')
    list_filter = ('payment_status', 'purchase_date_time', 'session__hall__cinema')
    search_fields = ('user__username', 'session__movie__title')
    autocomplete_fields = ['session', 'seat', 'user']

admin.site.register(Genres)
admin.site.register(Actors)

