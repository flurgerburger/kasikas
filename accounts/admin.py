from django.contrib import admin
from .models import Film, Ticket, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'studio_name', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'studio_name')


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'director', 'creator', 'category', 'status', 'views_count', 'ticket_price')
    list_filter = ('category', 'card_theme', 'status')
    search_fields = ('title', 'native_title', 'director', 'institution', 'synopsis')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'user', 'film', 'seats', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'film')
    search_fields = ('ticket_code', 'user__username', 'film__title')
