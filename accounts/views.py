from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def home(request):
	if not request.user.is_authenticated:
		return redirect('login')
	return render(request, 'home.html')


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
