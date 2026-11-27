from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('browse/', views.browse_films, name='browse'),
    path('films/<int:film_id>/', views.film_detail, name='film_detail'),
    path('films/<int:film_id>/watch/', views.watch_film, name='watch_film'),
    path('films/<int:film_id>/book/', views.book_ticket, name='book_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('profile/', views.profile_view, name='profile'),
    path('creator/', views.creator_dashboard, name='creator_dashboard'),
    path('creator/films/<int:film_id>/edit/', views.edit_film, name='edit_film'),
    path('creator/films/<int:film_id>/toggle-status/', views.toggle_film_status, name='toggle_film_status'),
    path('platform-admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
