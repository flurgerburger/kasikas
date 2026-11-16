from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .models import Film, Ticket


def home(request):
    films = Film.objects.all()
    return render(request, 'home.html', {'films': films})


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to Kasikas.')
        return redirect('home')
    return render(request, 'register.html', {'form': form})


def film_detail(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    return render(request, 'film_detail.html', {'film': film})


@login_required
def watch_film(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    return render(request, 'watch.html', {'film': film})


@login_required
def book_ticket(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    if request.method == 'POST':
        try:
            seats = int(request.POST.get('seats', 1))
        except (ValueError, TypeError):
            seats = 1
        seats = max(1, min(seats, 10))
        ticket = Ticket.objects.create(
            user=request.user,
            film=film,
            seats=seats
        )
        messages.success(
            request,
            f"Pass confirmed for '{film.title}'! Pass #{str(ticket.ticket_code)[:8].upper()} is in your reel."
        )
        return redirect('my_tickets')
    return redirect('film_detail', film_id=film.id)


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('film')
    return render(request, 'my_tickets.html', {'tickets': tickets})
