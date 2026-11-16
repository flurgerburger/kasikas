from django.contrib import admin
from .models import Film, Ticket


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'native_title', 'director', 'category', 'runtime_minutes', 'screening_venue', 'ticket_price')
    list_filter = ('category', 'card_theme')
    search_fields = ('title', 'native_title', 'director', 'institution', 'synopsis')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'user', 'film', 'seats', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'film')
    search_fields = ('ticket_code', 'user__username', 'film__title')
