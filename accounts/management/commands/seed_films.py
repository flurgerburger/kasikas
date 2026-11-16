from django.core.management.base import BaseCommand
from accounts.models import Film


class Command(BaseCommand):
    help = 'Populates the database with realistic seed Cebuano films for Kasikas'

    def handle(self, *args, **options):
        films_data = [
            {
                'title': 'Mga Dalan sa Gabii',
                'native_title': 'Mga Dalan sa Gabii (Streets of the Night)',
                'director': 'Bea Carillo',
                'institution': 'University of the Philippines Cebu (UP Cebu)',
                'category': 'SHORT',
                'runtime_minutes': 14,
                'logline': 'A quiet walk through the city after the last jeepney.',
                'synopsis': (
                    'A reflective slow-cinema journey through the dim avenues of Downtown Cebu after the last '
                    '04C jeepney completes its route. Captured in raw naturalistic night-lighting, the film explores '
                    'transient urban loneliness, quiet conversations, and the fleeting connections forged over shared '
                    'pungko-pungko benches along Colon Street.'
                ),
                'cast_and_crew': (
                    'Director: Bea Carillo\n'
                    'Cinematography: Jude Martinez\n'
                    'Sound Design: Lorenzo Alviola\n'
                    'Cast: Marco Abellana, Clarisse Yap'
                ),
                'card_theme': 'card-coral',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
                'screening_venue': 'Cinema Sugbo (Microcinema), Mango Square, Cebu City',
                'screening_time': 'Friday, 7:30 PM',
                'ticket_price': 150.00,
            },
            {
                'title': 'Asin ug Hangin',
                'native_title': 'Asin ug Hangin (Salt and Wind)',
                'director': 'Kyle Navarro',
                'institution': 'University of San Carlos (USC Talamban)',
                'category': 'THESIS',
                'runtime_minutes': 22,
                'logline': 'Three sisters return to the coast where they grew up.',
                'synopsis': (
                    'Three estranged sisters return to their ancestral coastal homestead in Bantayan Island following '
                    'their grandfather’s passing. Surrounded by the quiet rhythm of the tides and drying fish racks, '
                    'unspoken grievances surface over land titles, forgotten promises, and the burden of leaving Cebu '
                    'for opportunities overseas.'
                ),
                'cast_and_crew': (
                    'Director: Kyle Navarro\n'
                    'Screenplay: Anika Gonzaga\n'
                    'Production Design: Paolo Cinco\n'
                    'Cast: Theresa Suico, Patricia Montebon, Joylyn Tan'
                ),
                'card_theme': 'card-green',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
                'screening_venue': 'UP Cebu Performing Arts Hall, Gorordo Ave, Lahug',
                'screening_time': 'Saturday, 5:00 PM',
                'ticket_price': 120.00,
            },
            {
                'title': 'Ang Panaw',
                'native_title': 'Ang Panaw (The Passage)',
                'director': 'Dominic Villamor',
                'institution': 'Cebu Independent Filmmakers Guild',
                'category': 'DOCU',
                'runtime_minutes': 31,
                'logline': 'Portraits of the people who keep Carbon Market awake.',
                'synopsis': (
                    'A deeply rhythmic observational documentary chronicling the nocturnal ecosystem of Carbon Market. '
                    'From the midnight arrival of wooden bancas carrying fresh produce from Dalaguete and Bohol to the '
                    'first morning bell at the fruit stalls, this film is an ode to the tireless Visayan labor force that '
                    'feeds Cebu.'
                ),
                'cast_and_crew': (
                    'Director & Camera: Dominic Villamor\n'
                    'Editor: Renz Cañete\n'
                    'Soundscape: Visayan Ambient Collective'
                ),
                'card_theme': 'card-yellow',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
                'screening_venue': 'Robinsons Galleria Cebu Cinema Lounge',
                'screening_time': 'Sunday, 6:30 PM',
                'ticket_price': 180.00,
            },
        ]

        count = 0
        for data in films_data:
            film, created = Film.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Created film: {film.title}"))
            else:
                for key, value in data.items():
                    setattr(film, key, value)
                film.save()
                self.stdout.write(f"Updated existing film: {film.title}")

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {len(films_data)} films ({count} newly created)."))
