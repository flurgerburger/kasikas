from django import forms
from .models import Film


class FilmUploadForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = [
            'title',
            'native_title',
            'director',
            'institution',
            'category',
            'runtime_minutes',
            'logline',
            'synopsis',
            'director_note',
            'cast_and_crew',
            'card_theme',
            'thumbnail_file',
            'video_file',
            'video_url',
            'screening_venue',
            'screening_time',
            'ticket_price',
            'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Pagbalik sa Sugbo'}),
            'native_title': forms.TextInput(attrs={'placeholder': 'Optional Cebuano / Visayan title'}),
            'director': forms.TextInput(attrs={'placeholder': 'Director name'}),
            'institution': forms.TextInput(attrs={'placeholder': 'e.g., UP Cebu / Indie Collective'}),
            'runtime_minutes': forms.NumberInput(attrs={'min': 1, 'max': 240}),
            'logline': forms.TextInput(attrs={'placeholder': 'One-sentence pitch shown on catalog cards'}),
            'synopsis': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Full film synopsis...'}),
            'director_note': forms.Textarea(attrs={'rows': 3, 'placeholder': "Director's note or creative background (optional)..."}),
            'cast_and_crew': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Director: ...\nLead Cast: ...\nCinematography: ...\nEditor: ...\nSound Design: ...'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'https://... (optional if uploading video file)'}),
            'screening_venue': forms.TextInput(attrs={'placeholder': 'Cinema Sugbo, Cebu City'}),
            'screening_time': forms.TextInput(attrs={'placeholder': 'Friday, 7:00 PM'}),
            'ticket_price': forms.NumberInput(attrs={'min': '0', 'step': '10.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['video_url'].required = False
        self.fields['native_title'].required = False
        self.fields['institution'].required = False
        self.fields['director_note'].required = False
        self.fields['cast_and_crew'].required = False
        self.fields['thumbnail_file'].required = False
        self.fields['video_file'].required = False

    def clean_video_url(self):
        url = self.cleaned_data.get('video_url')
        if not url:
            return 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4'
        return url


class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First name'}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last name'}),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )
    studio_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Sugbo Indie Collective'}),
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell the Cebuano film community about yourself...'}),
    )
