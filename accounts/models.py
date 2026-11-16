import uuid
from django.db import models
from django.contrib.auth.models import User


class Film(models.Model):
    CATEGORY_CHOICES = [
        ('SHORT', 'Short Film'),
        ('THESIS', 'Student Thesis'),
        ('DOCU', 'Documentary'),
        ('FEATURE', 'Feature'),
    ]

    COLOR_CHOICES = [
        ('card-coral', 'Coral'),
        ('card-green', 'Green'),
        ('card-yellow', 'Yellow'),
    ]

    title = models.CharField(max_length=200)
    native_title = models.CharField(max_length=200, blank=True, help_text="Visayan / Cebuano title if applicable")
    director = models.CharField(max_length=150)
    institution = models.CharField(max_length=150, blank=True, help_text="e.g., University of San Carlos (USC), UP Cebu")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='SHORT')
    runtime_minutes = models.PositiveIntegerField(default=15)
    logline = models.CharField(max_length=255, help_text="Short one-line pitch for cards")
    synopsis = models.TextField(help_text="Full film synopsis / director's note")
    cast_and_crew = models.TextField(blank=True, help_text="Comma-separated or multiline credits")
    card_theme = models.CharField(max_length=20, choices=COLOR_CHOICES, default='card-coral')
    video_url = models.URLField(
        default="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        help_text="Direct MP4 URL or stream link for playback"
    )
    screening_venue = models.CharField(max_length=200, default="Cinema Sugbo, Cebu City")
    screening_time = models.CharField(max_length=100, default="Friday, 7:00 PM")
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2, default=150.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    @property
    def category_meta(self):
        cat_display = dict(self.CATEGORY_CHOICES).get(self.category, self.category).upper()
        return f"{cat_display} / {self.runtime_minutes} MIN"


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
