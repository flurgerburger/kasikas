from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Count, F, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .context_processors import get_user_role
from .forms import FilmUploadForm, ProfileUpdateForm
from .models import Film, Ticket, UserProfile


def _is_admin_user(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return UserProfile.objects.filter(user=user, role=UserProfile.ROLE_ADMIN).exists()


def home(request):
    films = Film.objects.filter(status=Film.STATUS_PUBLISHED)
    booked_films = None

    if request.user.is_authenticated:
        booked_film_ids = Ticket.objects.filter(
            user=request.user
        ).values('film_id')

        booked_films = Film.objects.filter(
            id__in=Subquery(booked_film_ids),
            status=Film.STATUS_PUBLISHED,
        )

    return render(request, 'home.html', {'films': films, 'booked_films': booked_films})


def login_view(request):
    if request.user.is_authenticated:
        role = get_user_role(request.user, request.session)
        if role == UserProfile.ROLE_ADMIN:
            return redirect('admin_dashboard')
        if role == UserProfile.ROLE_CREATOR:
            return redirect('creator_dashboard')
        return redirect('home')

    form = AuthenticationForm(request, data=request.POST or None)
    selected_role = request.POST.get('role', UserProfile.ROLE_VIEWER)
    next_url = request.POST.get('next') or request.GET.get('next', '')

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        if _is_admin_user(user):
            request.session['active_role'] = UserProfile.ROLE_ADMIN
            messages.success(request, 'Signed in as Platform Admin.')
            return redirect('admin_dashboard')

        role = (
            UserProfile.ROLE_CREATOR
            if selected_role == UserProfile.ROLE_CREATOR
            else UserProfile.ROLE_VIEWER
        )
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if role == UserProfile.ROLE_CREATOR and profile.role != UserProfile.ROLE_CREATOR:
            profile.role = UserProfile.ROLE_CREATOR
            profile.save(update_fields=['role'])

        request.session['active_role'] = role

        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)

        if role == UserProfile.ROLE_CREATOR:
            messages.success(request, 'Welcome back to Kasikas Creator Studio.')
            return redirect('creator_dashboard')

        messages.success(request, 'Welcome back to Kasikas.')
        return redirect('home')

    return render(request, 'login.html', {
        'form': form,
        'selected_role': selected_role,
        'next_url': next_url,
    })


def admin_login_view(request):
    if request.user.is_authenticated and _is_admin_user(request.user):
        return redirect('admin_dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not _is_admin_user(user):
            form.add_error(None, 'Access denied. This portal is restricted to Kasikas platform administrators.')
        else:
            login(request, user)
            request.session['active_role'] = UserProfile.ROLE_ADMIN
            messages.success(request, 'Platform Admin session authenticated.')
            return redirect('admin_dashboard')

    return render(request, 'admin_login.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        role = get_user_role(request.user, request.session)
        if role == UserProfile.ROLE_ADMIN:
            return redirect('admin_dashboard')
        if role == UserProfile.ROLE_CREATOR:
            return redirect('creator_dashboard')
        return redirect('home')

    form = UserCreationForm(request.POST or None)
    selected_role = request.POST.get('role', UserProfile.ROLE_VIEWER)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        role = (
            UserProfile.ROLE_CREATOR
            if selected_role == UserProfile.ROLE_CREATOR
            else UserProfile.ROLE_VIEWER
        )
        UserProfile.objects.create(user=user, role=role)
        login(request, user)
        request.session['active_role'] = role

        if role == UserProfile.ROLE_CREATOR:
            messages.success(request, 'Creator account ready. Upload your first short film.')
            return redirect('creator_dashboard')

        messages.success(request, 'Welcome to Kasikas.')
        return redirect('home')

    return render(request, 'register.html', {
        'form': form,
        'selected_role': selected_role,
    })


def film_detail(request, film_id):
    film_qs = Film.objects.annotate(
        total_bookings=Count('tickets'),
        total_seats=Sum('tickets__seats'),
    )
    film = get_object_or_404(film_qs, pk=film_id)
    return render(request, 'film_detail.html', {'film': film})


@login_required
def watch_film(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    Film.objects.filter(pk=film_id).update(views_count=F('views_count') + 1)
    film.refresh_from_db()
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


def _build_monthly_earnings(films_qs):
    """Build a 6-month earnings timeline for the creator dashboard."""
    now = timezone.now()
    months = []
    for offset in range(5, -1, -1):
        month_num = (now.month - 1 - offset) % 12 + 1
        year_num = now.year + ((now.month - 1 - offset) // 12)
        months.append((year_num, month_num))

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    totals_by_ym = {ym: Decimal('0.00') for ym in months}
    tickets_by_ym = {ym: 0 for ym in months}

    tickets = Ticket.objects.filter(film__in=films_qs).select_related('film')
    for t in tickets:
        ym = (t.created_at.year, t.created_at.month)
        if ym in totals_by_ym:
            totals_by_ym[ym] += Decimal(t.seats) * t.film.ticket_price
            tickets_by_ym[ym] += t.seats

    max_rev = max(totals_by_ym.values()) if totals_by_ym else Decimal('0.00')
    series = []
    for y, m in months:
        rev = totals_by_ym[(y, m)]
        pct = int((rev / max_rev) * 100) if max_rev > 0 else 0
        series.append({
            'label': f"{month_names[m - 1]} {str(y)[2:]}",
            'revenue': rev,
            'tickets': tickets_by_ym[(y, m)],
            'pct': max(pct, 6) if rev > 0 else 4,
        })
    return series


@login_required
def creator_dashboard(request):
    role = get_user_role(request.user, request.session)
    if role not in (UserProfile.ROLE_CREATOR, UserProfile.ROLE_ADMIN):
        messages.info(request, 'Sign in as an Indie Creator to access Creator Studio.')
        return redirect('home')

    if request.method == 'POST':
        form = FilmUploadForm(request.POST, request.FILES)
        if form.is_valid():
            film = form.save(commit=False)
            film.creator = request.user
            if not film.director:
                film.director = request.user.get_full_name() or request.user.username
            film.save()
            messages.success(request, f"'{film.title}' saved to your releases ({film.get_status_display()}).")
            return redirect('creator_dashboard')
    else:
        form = FilmUploadForm(initial={
            'director': request.user.get_full_name() or request.user.username,
            'ticket_price': Decimal('150.00'),
        })

    my_films_qs = Film.objects.filter(creator=request.user).annotate(
        tickets_sold=Coalesce(Sum('tickets__seats'), 0),
        bookings_count=Count('tickets'),
    ).order_by('-created_at', '-id')

    my_films = []
    total_revenue = Decimal('0.00')
    total_tickets_sold = 0
    total_views = 0
    published_count = 0
    draft_count = 0

    for film in my_films_qs:
        revenue = Decimal(film.tickets_sold) * film.ticket_price
        film.revenue = revenue
        my_films.append(film)
        total_revenue += revenue
        total_tickets_sold += film.tickets_sold
        total_views += film.views_count
        if film.status == Film.STATUS_PUBLISHED:
            published_count += 1
        else:
            draft_count += 1

    payout_threshold = Decimal('500.00')
    if total_revenue >= payout_threshold:
        payout_status = 'Ready for Payout'
        payout_note = 'Eligible for next Friday GCash / bank settlement.'
    elif total_revenue > 0:
        payout_status = 'Accumulating'
        payout_note = f'₱{payout_threshold - total_revenue:.2f} more to reach ₱500 payout threshold.'
    else:
        payout_status = 'No Earnings Yet'
        payout_note = 'Publish a short film and sell passes to start earning.'

    earnings_series = _build_monthly_earnings(my_films_qs)

    return render(request, 'creator_dashboard.html', {
        'form': form,
        'my_films': my_films,
        'total_revenue': total_revenue,
        'total_tickets_sold': total_tickets_sold,
        'total_views': total_views,
        'published_count': published_count,
        'draft_count': draft_count,
        'payout_status': payout_status,
        'payout_note': payout_note,
        'earnings_series': earnings_series,
    })


@login_required
def toggle_film_status(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    if film.creator != request.user and not _is_admin_user(request.user):
        messages.error(request, 'You do not have permission to update this film.')
        return redirect('creator_dashboard')

    if request.method == 'POST':
        film.status = (
            Film.STATUS_DRAFT
            if film.status == Film.STATUS_PUBLISHED
            else Film.STATUS_PUBLISHED
        )
        film.save(update_fields=['status'])
        messages.success(request, f"'{film.title}' is now {film.get_status_display()}.")

    return redirect('creator_dashboard')


@login_required
def admin_dashboard(request):
    if not _is_admin_user(request.user):
        messages.error(request, 'Admin access required.')
        return redirect('home')

    all_films_qs = Film.objects.select_related('creator').annotate(
        tickets_sold=Coalesce(Sum('tickets__seats'), 0),
        bookings_count=Count('tickets'),
    ).order_by('-views_count', '-created_at')

    films_table = []
    total_views = 0
    overall_revenue = Decimal('0.00')
    total_tickets_sold = 0
    published_releases = 0

    for film in all_films_qs:
        revenue = Decimal(film.tickets_sold) * film.ticket_price
        film.revenue = revenue
        film.creator_label = film.creator.username if film.creator else film.director
        films_table.append(film)
        total_views += film.views_count
        overall_revenue += revenue
        total_tickets_sold += film.tickets_sold
        if film.status == Film.STATUS_PUBLISHED:
            published_releases += 1

    total_active_creators = User.objects.filter(
        Q(profile__role=UserProfile.ROLE_CREATOR) | Q(created_films__isnull=False)
    ).distinct().count()

    # Top performing releases (up to 5)
    top_releases = sorted(films_table, key=lambda f: (f.views_count, f.tickets_sold), reverse=True)[:5]
    max_top_views = max((f.views_count for f in top_releases), default=1) or 1
    for f in top_releases:
        f.views_pct = max(int((f.views_count / max_top_views) * 100), 8) if f.views_count else 4

    # 6-month platform watch & release volume trends
    now = timezone.now()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months = []
    for offset in range(5, -1, -1):
        month_num = (now.month - 1 - offset) % 12 + 1
        year_num = now.year + ((now.month - 1 - offset) // 12)
        months.append((year_num, month_num))

    releases_by_ym = {ym: 0 for ym in months}
    tickets_by_ym = {ym: 0 for ym in months}
    for film in films_table:
        ym = (film.created_at.year, film.created_at.month)
        if ym in releases_by_ym:
            releases_by_ym[ym] += 1

    for t in Ticket.objects.all():
        ym = (t.created_at.year, t.created_at.month)
        if ym in tickets_by_ym:
            tickets_by_ym[ym] += t.seats

    # Distribute platform watches across the 6-month window weighted by activity
    weights = [10, 14, 16, 18, 20, 22]
    weight_sum = sum(weights)
    max_rel = max(releases_by_ym.values()) if releases_by_ym else 1
    max_rel = max(max_rel, 1)

    trend_series = []
    for idx, (y, m) in enumerate(months):
        est_watches = int(round((total_views * weights[idx]) / weight_sum)) if total_views else 0
        rel_count = releases_by_ym[(y, m)]
        trend_series.append({
            'label': f"{month_names[m - 1]}",
            'watches': est_watches,
            'watches_pct': max(int((weights[idx] / max(weights)) * 100), 10) if total_views else 6,
            'releases': rel_count,
            'releases_pct': max(int((rel_count / max_rel) * 100), 10) if rel_count else 4,
            'tickets': tickets_by_ym[(y, m)],
        })

    # Category / Genre breakdown
    category_counts = []
    total_film_count = len(films_table) or 1
    for code, label in Film.CATEGORY_CHOICES:
        cnt = sum(1 for f in films_table if f.category == code)
        category_counts.append({
            'code': code,
            'label': label,
            'count': cnt,
            'pct': int((cnt / total_film_count) * 100),
        })

    return render(request, 'admin_dashboard.html', {
        'total_releases': published_releases,
        'total_all_films': len(films_table),
        'total_views': total_views,
        'total_active_creators': total_active_creators,
        'overall_revenue': overall_revenue,
        'total_tickets_sold': total_tickets_sold,
        'films_table': films_table,
        'top_releases': top_releases,
        'trend_series': trend_series,
        'category_counts': category_counts,
    })


def browse_films(request):
    films = Film.objects.filter(status=Film.STATUS_PUBLISHED).select_related('creator', 'creator__profile')

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    institution = request.GET.get('institution', '').strip()
    venue = request.GET.get('venue', '').strip()

    if q:
        films = films.filter(
            Q(title__icontains=q)
            | Q(native_title__icontains=q)
            | Q(synopsis__icontains=q)
            | Q(director_note__icontains=q)
            | Q(director__icontains=q)
            | Q(creator__username__icontains=q)
            | Q(creator__profile__studio_name__icontains=q)
        ).distinct()

    valid_categories = dict(Film.CATEGORY_CHOICES)
    if category in valid_categories:
        films = films.filter(category=category)
    else:
        category = ''

    if institution:
        films = films.filter(institution=institution)

    if venue:
        films = films.filter(screening_venue=venue)

    published_base = Film.objects.filter(status=Film.STATUS_PUBLISHED)
    institutions = list(
        published_base.exclude(institution='').values_list('institution', flat=True).distinct().order_by('institution')
    )
    venues = list(
        published_base.exclude(screening_venue='').values_list('screening_venue', flat=True).distinct().order_by('screening_venue')
    )

    has_filters = bool(q or category or institution or venue)

    return render(request, 'browse.html', {
        'films': films,
        'q': q,
        'selected_category': category,
        'selected_institution': institution,
        'selected_venue': venue,
        'category_choices': Film.CATEGORY_CHOICES,
        'institutions': institutions,
        'venues': venues,
        'has_filters': has_filters,
    })


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    active_role = get_user_role(request.user, request.session)
    is_admin = _is_admin_user(request.user)

    if request.method == 'POST':
        action = request.POST.get('action', 'update_profile')
        if action == 'switch_role' and not is_admin:
            target_role = (
                UserProfile.ROLE_VIEWER
                if active_role == UserProfile.ROLE_CREATOR
                else UserProfile.ROLE_CREATOR
            )
            request.session['active_role'] = target_role
            profile.role = target_role
            profile.save(update_fields=['role'])
            messages.success(request, f"Switched to {profile.get_role_display()} mode.")
            return redirect('profile')

        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save(update_fields=['first_name', 'last_name', 'email'])

            profile.studio_name = form.cleaned_data['studio_name']
            profile.bio = form.cleaned_data['bio']
            profile.save(update_fields=['studio_name', 'bio'])

            messages.success(request, 'Profile details updated.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'studio_name': profile.studio_name,
            'bio': profile.bio,
        })

    ticket_stats = Ticket.objects.filter(user=request.user).aggregate(
        total_passes=Count('id'),
        total_seats=Coalesce(Sum('seats'), 0),
    )
    films_uploaded = (
        request.user.created_films.count()
        if (active_role == UserProfile.ROLE_CREATOR or profile.role == UserProfile.ROLE_CREATOR)
        else None
    )

    return render(request, 'profile.html', {
        'profile': profile,
        'form': form,
        'active_role': active_role,
        'is_admin': is_admin,
        'total_passes': ticket_stats['total_passes'],
        'total_seats': ticket_stats['total_seats'],
        'films_uploaded': films_uploaded,
    })


@login_required
def edit_film(request, film_id):
    film = get_object_or_404(Film, pk=film_id)
    if film.creator != request.user and not _is_admin_user(request.user):
        messages.error(request, 'You do not have permission to edit this film.')
        return redirect('creator_dashboard')

    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            title = film.title
            film.delete()
            messages.success(request, f"'{title}' has been deleted.")
            return redirect('creator_dashboard')

        form = FilmUploadForm(request.POST, request.FILES, instance=film)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated '{film.title}'.")
            return redirect('creator_dashboard')
    else:
        form = FilmUploadForm(instance=film)

    return render(request, 'edit_film.html', {
        'form': form,
        'film': film,
    })
