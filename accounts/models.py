import uuid
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_VIEWER = 'VIEWER'
    ROLE_CREATOR = 'CREATOR'
    ROLE_ADMIN = 'ADMIN'

    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Viewer'),
        (ROLE_CREATOR, 'Indie Creator'),
        (ROLE_ADMIN, 'Platform Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default=ROLE_VIEWER)
    studio_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Film(models.Model):
    CATEGORY_CHOICES = [
        ('SHORT', 'Short Film'),
        ('THESIS', 'Student Thesis'),
        ('DOCU', 'Documentary'),
        ('FEATURE', 'Feature'),
    ]

    COLOR_CHOICES = [
        ('theme-noir', 'Noir Monochrome'),
        ('theme-gold', 'Warm Indie Gold'),
        ('theme-cyber', 'Neon Cyberpunk'),
        ('theme-vintage', 'Vintage Film Grain'),
        ('theme-coastal', 'Coastal Teal'),
        ('theme-crimson', 'Crimson Drama'),
        ('card-coral', 'Coral'),
        ('card-green', 'Green'),
        ('card-yellow', 'Yellow'),
    ]

    THEME_METADATA = {
        'theme-noir': {'label': 'Noir Monochrome', 'tag': 'NOIR'},
        'theme-gold': {'label': 'Warm Indie Gold', 'tag': 'INDIE GOLD'},
        'theme-cyber': {'label': 'Neon Cyberpunk', 'tag': 'NEON'},
        'theme-vintage': {'label': 'Vintage Film Grain', 'tag': '35MM GRAIN'},
        'theme-coastal': {'label': 'Coastal Teal', 'tag': 'COASTAL'},
        'theme-crimson': {'label': 'Crimson Drama', 'tag': 'CRIMSON'},
        'card-coral': {'label': 'Terracotta Coral', 'tag': 'CORAL'},
        'card-green': {'label': 'Forest Green', 'tag': 'EMERALD'},
        'card-yellow': {'label': 'Amber Ochre', 'tag': 'AMBER'},
    }

    STATUS_PUBLISHED = 'PUBLISHED'
    STATUS_DRAFT = 'DRAFT'
    STATUS_CHOICES = [
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_DRAFT, 'Draft'),
    ]

    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_films',
    )
    title = models.CharField(max_length=200)
    native_title = models.CharField(max_length=200, blank=True, help_text="Visayan / Cebuano title if applicable")
    director = models.CharField(max_length=150)
    institution = models.CharField(max_length=150, blank=True, help_text="e.g., University of San Carlos (USC), UP Cebu")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='SHORT')
    runtime_minutes = models.PositiveIntegerField(default=15)
    logline = models.CharField(max_length=255, help_text="Short one-line pitch for cards")
    synopsis = models.TextField(help_text="Full film synopsis")
    director_note = models.TextField(blank=True, help_text="Director's note or creative background for festival program")
    cast_and_crew = models.TextField(blank=True, help_text="Comma-separated or multiline credits")
    card_theme = models.CharField(max_length=20, choices=COLOR_CHOICES, default='theme-gold')
    video_url = models.URLField(
        default="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        help_text="Direct MP4 URL or stream link for playback"
    )
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    thumbnail_file = models.FileField(upload_to='thumbnails/', blank=True, null=True)
    screening_venue = models.CharField(max_length=200, default="Cinema Sugbo, Cebu City")
    screening_time = models.CharField(max_length=100, default="Friday, 7:00 PM")
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2, default=150.00)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    @property
    def category_meta(self):
        cat_display = dict(self.CATEGORY_CHOICES).get(self.category, self.category).upper()
        return f"{cat_display} / {self.runtime_minutes} MIN"

    @property
    def playback_url(self):
        if self.video_file:
            return self.video_file.url
        return self.video_url

    @property
    def thumbnail_src(self):
        if self.thumbnail_file:
            return self.thumbnail_file.url
        return ''

    @property
    def theme_meta(self):
        return self.THEME_METADATA.get(
            self.card_theme,
            {'label': 'Warm Indie Gold', 'tag': 'INDIE'},
        )

    @property
    def parsed_credits(self):
        """Parse multiline 'Role: Name' credits into structured (role, name) dicts."""
        credits_list = []
        if not self.cast_and_crew:
            return credits_list
        for raw_line in self.cast_and_crew.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if ':' in line:
                role, names = line.split(':', 1)
                credits_list.append({'role': role.strip(), 'names': names.strip()})
            else:
                credits_list.append({'role': 'Credit', 'names': line})
        return credits_list


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='tickets')
    ticket_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    seats = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{str(self.ticket_code)[:8]} - {self.film.title} ({self.user.username})"
