from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Genres, Actors, Movies, Cinemas, Halls, Sessions, Seats, Tickets, Order, MovieBadges
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

class TicketsInline(admin.TabularInline):
    model = Tickets
    fields = ('session', 'seat', 'price', 'is_cancelled')
    readonly_fields = ('session', 'seat', 'price')
    autocomplete_fields = ['session', 'seat']
    extra = 0
    can_delete = False

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
    list_display = ('__str__', 'movie', 'hall', 'start_time', 'end_time', 'price', 'is_active')
    list_filter = ('start_time','end_time', 'hall__cinema', 'movie', 'is_active')
    search_fields = ('movie__title', 'hall__name')
    autocomplete_fields = ['movie', 'hall']

@admin.register(Seats)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'hall')
    list_filter = ('hall__cinema', 'hall')
    search_fields = ('hall__name', 'hall__cinema__name', 'row', 'num')
    autocomplete_fields = ['hall']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketsInline]
    list_display = ('id', 'user', 'status', 'total_amount', 'get_ticket_count', 'created_at', 'liqpay_order_id')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'liqpay_order_id')
    autocomplete_fields = ['user']
    date_hierarchy = 'created_at'

    readonly_fields = ('user', 'liqpay_order_id', 'created_at', 'total_amount')

    @admin.display(ordering='Кількість квитків')
    def get_ticket_count(self, obj):
        return obj.tickets.count()

@admin.register(Tickets)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user', 'session', 'seat', 'get_payment_status', 'is_cancelled')
    list_filter = ('order__status', 'is_cancelled', 'order__created_at', 'session__hall__cinema')
    search_fields = ('order__user__username', 'session__movie__title', 'order__liqpay_order_id')
    autocomplete_fields = ['order', 'session', 'seat']

    @admin.display(description='Користувач', ordering='order__user')
    def get_user(self, obj):
        return obj.order.user

    @admin.display(description='Статус оплати', ordering='order__status')
    def get_payment_status(self, obj):
        return obj.order.status

admin.site.register(Genres)
admin.site.register(Actors)

