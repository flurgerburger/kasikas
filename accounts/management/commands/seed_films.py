from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from accounts.models import Film, Ticket, UserProfile


class Command(BaseCommand):
    help = 'Populates the database with 12+ realistic indie short films, directors, cast/crew, themes, and sample tickets for Kasikas'

    def _ensure_user(self, username, email, password, role, is_staff=False, is_superuser=False, studio_name='', bio=''):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': is_staff, 'is_superuser': is_superuser},
        )
        if created:
            user.set_password(password)
        user.email = email
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        if studio_name:
            profile.studio_name = studio_name
        if bio:
            profile.bio = bio
        profile.save()
        return user

    def handle(self, *args, **options):
        admin_user = self._ensure_user(
            'admin', 'admin@kasikas.ph', 'AdminPass123!',
            UserProfile.ROLE_ADMIN, is_staff=True, is_superuser=True,
            studio_name='Kasikas Operations',
        )
        bea_creator = self._ensure_user(
            'bea_creator', 'bea@kasikas.ph', 'CreatorPass123!',
            UserProfile.ROLE_CREATOR,
            studio_name='Colon Street Frames',
            bio='Cebuano slow-cinema filmmaker exploring nocturnal urban life and sensory storytelling.',
        )
        kyle_creator = self._ensure_user(
            'kyle_creator', 'kyle@kasikas.ph', 'CreatorPass123!',
            UserProfile.ROLE_CREATOR,
            studio_name='Bantayan Tide Films',
            bio='Director and writer focusing on coastal family dramas across northern Cebu.',
        )
        dominic_creator = self._ensure_user(
            'dominic_creator', 'dominic@kasikas.ph', 'CreatorPass123!',
            UserProfile.ROLE_CREATOR,
            studio_name='Visayan Lens Collective',
            bio='Observational documentarian capturing working-class rhythms in Cebu markets and ports.',
        )
        marisol_creator = self._ensure_user(
            'marisol_creator', 'marisol@kasikas.ph', 'CreatorPass123!',
            UserProfile.ROLE_CREATOR,
            studio_name='Sugbo Neon Lab',
            bio='Genre and experimental filmmaker blending cyberpunk aesthetics with Bisaya folklore.',
        )
        rafael_creator = self._ensure_user(
            'rafael_creator', 'rafael@kasikas.ph', 'CreatorPass123!',
            UserProfile.ROLE_CREATOR,
            studio_name='Mactan Celluloid',
            bio='Archival 16mm and Super 8 enthusiast telling intimate coming-of-age stories.',
        )
        viewer_user = self._ensure_user(
            'cebu_viewer', 'viewer@kasikas.ph', 'ViewerPass123!',
            UserProfile.ROLE_VIEWER,
        )

        films_data = [
            {
                'creator': bea_creator,
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
                'director_note': (
                    'Shot entirely between 1:00 AM and 4:30 AM using available sodium-vapor streetlamps, '
                    'Mga Dalan sa Gabii is a love letter to the nocturnal commuters and night-shift workers '
                    'who keep Cebu breathing long after the malls lock their doors.'
                ),
                'cast_and_crew': (
                    'Director: Bea Carillo\n'
                    'Lead Cast: Marco Abellana, Clarisse Yap\n'
                    'Cinematographer: Jude Martinez\n'
                    'Editor: Camille Dizon\n'
                    'Sound Designer: Lorenzo Alviola'
                ),
                'card_theme': 'theme-noir',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
                'screening_venue': 'Cinema Sugbo (Microcinema), Mango Square, Cebu City',
                'screening_time': 'Friday, 7:30 PM',
                'ticket_price': 150.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 1420,
            },
            {
                'creator': kyle_creator,
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
                'director_note': (
                    'Growing up in a fishing barangay, I wanted the ocean to act as a fourth sister—patient, '
                    'unforgiving, and ever-present. We recorded live coastal wind and surf on location to anchor '
                    'every silence between the characters.'
                ),
                'cast_and_crew': (
                    'Director: Kyle Navarro\n'
                    'Lead Cast: Theresa Suico, Patricia Montebon, Joylyn Tan\n'
                    'Cinematographer: Mateo Rosales\n'
                    'Editor: Hannah Lim\n'
                    'Sound Designer: Nico Solis'
                ),
                'card_theme': 'theme-coastal',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
                'screening_venue': 'UP Cebu Performing Arts Hall, Gorordo Ave, Lahug',
                'screening_time': 'Saturday, 5:00 PM',
                'ticket_price': 120.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 980,
            },
            {
                'creator': dominic_creator,
                'title': 'Ang Panaw',
                'native_title': 'Ang Panaw (The Passage)',
                'director': 'Dominic Villamor',
                'institution': 'Visayan Lens Collective',
                'category': 'DOCU',
                'runtime_minutes': 31,
                'logline': 'Portraits of the people who keep Carbon Market awake.',
                'synopsis': (
                    'A deeply rhythmic observational documentary chronicling the nocturnal ecosystem of Carbon Market. '
                    'From the midnight arrival of wooden bancas carrying fresh produce from Dalaguete and Bohol to the '
                    'first morning bell at the fruit stalls, this film is an ode to the tireless Visayan labor force that '
                    'feeds Cebu.'
                ),
                'director_note': (
                    'We spent six weeks shadowing kargadors, flower vendors, and coffee cart owners without a script. '
                    'The edit follows the natural crescendo of a single market night from midnight calm to 6:00 AM rush.'
                ),
                'cast_and_crew': (
                    'Director: Dominic Villamor\n'
                    'Featured Subjects: Mang Nestor Bacalso, Aling Rosa Cabahug\n'
                    'Cinematographer: Dominic Villamor\n'
                    'Editor: Renz Cañete\n'
                    'Sound Designer: Visayan Ambient Collective'
                ),
                'card_theme': 'theme-gold',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
                'screening_venue': 'Robinsons Galleria Cebu Cinema Lounge',
                'screening_time': 'Sunday, 6:30 PM',
                'ticket_price': 180.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 2150,
            },
            {
                'creator': bea_creator,
                'title': 'Sinulog sa Kahilom',
                'native_title': 'Sinulog sa Kahilom (Dance in Silence)',
                'director': 'Bea Carillo',
                'institution': 'Colon Street Frames',
                'category': 'SHORT',
                'runtime_minutes': 18,
                'logline': 'A deaf percussionist prepares for the grand street parade.',
                'synopsis': (
                    'Feeling the bass of the drums through floorboards and asphalt, a young Cebuano percussionist '
                    'rehearses in the quiet hours before dawn ahead of the city’s biggest festival, determined to lead '
                    'her contingent by pulse and vibration alone.'
                ),
                'director_note': (
                    'Our sound design team worked closely with deaf musicians in Mandaue to translate sub-bass '
                    'tactile vibrations into cinema—shifting between near-total silence and visceral low-frequency rumble.'
                ),
                'cast_and_crew': (
                    'Director: Bea Carillo\n'
                    'Lead Cast: Pauline Quirante, Gabriel Yu\n'
                    'Cinematographer: Jude Martinez\n'
                    'Editor: Tessa Magno\n'
                    'Sound Designer: Lorenzo Alviola'
                ),
                'card_theme': 'theme-crimson',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
                'screening_venue': 'Cinema Sugbo (Microcinema), Mango Square, Cebu City',
                'screening_time': 'Saturday, 8:00 PM',
                'ticket_price': 160.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 740,
            },
            {
                'creator': marisol_creator,
                'title': 'Neon sa Mabolo',
                'native_title': 'Neon sa Mabolo (Neon in Mabolo)',
                'director': 'Marisol Uy',
                'institution': 'Sugbo Neon Lab',
                'category': 'SHORT',
                'runtime_minutes': 16,
                'logline': 'A motorcycle courier intercepts a coded cassette in rain-slicked Cebu.',
                'synopsis': (
                    'Set in a rain-drenched, near-future Cebu City where analog cassette tapes are used to smuggle '
                    'banned local music, a courier takes one last midnight delivery through Mabolo’s neon-lit flyovers '
                    'and finds a message meant for her missing brother.'
                ),
                'director_note': (
                    'I wanted to prove you can build a tactile sci-fi noir using Cebu’s real flyovers, wet asphalt, '
                    'and practical LED tubes—no CGI skylines, just pure Visayan street atmosphere.'
                ),
                'cast_and_crew': (
                    'Director: Marisol Uy\n'
                    'Lead Cast: Mikael Go, Dianne Sarmiento\n'
                    'Cinematographer: Kenji Velasco\n'
                    'Editor: Marisol Uy\n'
                    'Sound Designer: SynthSugbo'
                ),
                'card_theme': 'theme-cyber',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
                'screening_venue': 'Ayala Center Cebu Indie Lounge',
                'screening_time': 'Friday, 9:00 PM',
                'ticket_price': 170.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 1680,
            },
            {
                'creator': rafael_creator,
                'title': 'Karatula 1998',
                'native_title': 'Karatula 1998 (Signboard 1998)',
                'director': 'Rafael Ocampo',
                'institution': 'Mactan Celluloid',
                'category': 'THESIS',
                'runtime_minutes': 19,
                'logline': 'A hand-painted theater billboard artist faces the arrival of digital prints.',
                'synopsis': (
                    'In the summer of 1998, an aging movie billboard painter in downtown Cebu teaches his teenage '
                    'nephew how to mix oil pigments for towering cinema marquees, unaware that the theater’s management '
                    'has already ordered its final hand-painted canvas.'
                ),
                'director_note': (
                    'Inspired by the last generation of Cebuano signboard painters, we graded the digital negative '
                    'with custom 16mm halation and film grain to honor the warmth of late-90s provincial cinemas.'
                ),
                'cast_and_crew': (
                    'Director: Rafael Ocampo\n'
                    'Lead Cast: Arturo Ponce, Miguelito Chavez\n'
                    'Cinematographer: Antonette Lee\n'
                    'Editor: Rafael Ocampo\n'
                    'Sound Designer: Carlo Benedicto'
                ),
                'card_theme': 'theme-vintage',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                'screening_venue': 'Casa Gorordo Courtyard Screening, Parian',
                'screening_time': 'Sunday, 5:30 PM',
                'ticket_price': 140.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 1120,
            },
            {
                'creator': kyle_creator,
                'title': 'Balod sa Camotes',
                'native_title': 'Balod sa Camotes (Waves of Camotes)',
                'director': 'Kyle Navarro',
                'institution': 'Bantayan Tide Films',
                'category': 'SHORT',
                'runtime_minutes': 15,
                'logline': 'Two teenage divers search a sunken pier for a lost wedding ring.',
                'synopsis': (
                    'Before Typhoon season closes the ferry routes, two best friends dive beneath an abandoned wooden '
                    'pier in Camotes to recover a ring dropped by a visiting tourist—uncovering an old WWII brass '
                    'compass that tests their friendship.'
                ),
                'director_note': (
                    'Filmed 40% underwater with a custom housing, this short celebrates the crystal-clear shallows '
                    'of Camotes and the effortless humor of Bisaya youth.'
                ),
                'cast_and_crew': (
                    'Director: Kyle Navarro\n'
                    'Lead Cast: Nathan Alcaraz, Joshua Minoza\n'
                    'Cinematographer: Mateo Rosales\n'
                    'Editor: Hannah Lim\n'
                    'Sound Designer: Nico Solis'
                ),
                'card_theme': 'theme-coastal',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4',
                'screening_venue': 'SM Seaside City Cebu Directors Club',
                'screening_time': 'Saturday, 3:30 PM',
                'ticket_price': 150.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 890,
            },
            {
                'creator': marisol_creator,
                'title': 'Kabit sa Kuryente',
                'native_title': 'Kabit sa Kuryente (Tangled Wires)',
                'director': 'Marisol Uy',
                'institution': 'Sugbo Neon Lab',
                'category': 'SHORT',
                'runtime_minutes': 13,
                'logline': 'A rogue sound engineer records ghost frequencies from Cebu’s utility poles.',
                'synopsis': (
                    'Armed with a modified electromagnetic coil mic, a sleep-deprived audio archivist maps the tangled '
                    'overhead wires of Barangay Kamputhaw and begins hearing fragments of forgotten Bisaya radio dramas '
                    'embedded in the city’s 60Hz hum.'
                ),
                'director_note': (
                    'Every hum and crackle in the soundtrack was genuinely recorded from real Cebu City transformers '
                    'using induction pickups, then layered into a haunting electronic score.'
                ),
                'cast_and_crew': (
                    'Director: Marisol Uy\n'
                    'Lead Cast: Beaulah Tiu, Jericho Yap\n'
                    'Cinematographer: Kenji Velasco\n'
                    'Editor: Camille Dizon\n'
                    'Sound Designer: SynthSugbo'
                ),
                'card_theme': 'theme-cyber',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4',
                'screening_venue': 'Cinema Sugbo (Microcinema), Mango Square, Cebu City',
                'screening_time': 'Saturday, 9:30 PM',
                'ticket_price': 160.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 1340,
            },
            {
                'creator': dominic_creator,
                'title': 'Mga Kamot sa Mactan',
                'native_title': 'Mga Kamot sa Mactan (Hands of Mactan)',
                'director': 'Dominic Villamor',
                'institution': 'Visayan Lens Collective',
                'category': 'DOCU',
                'runtime_minutes': 26,
                'logline': 'Inside the family-run guitar workshops of Pajac, Lapu-Lapu.',
                'synopsis': (
                    'An intimate portrait of three generations of luthiers in Mactan who carve, bend, and varnish '
                    'acoustic guitars by hand. As mass-produced imports crowd the market, a father and daughter debate '
                    'whether to modernize or preserve their slow craft.'
                ),
                'director_note': (
                    'We miked the wood planes, chisels, and raw spruce tops like musical instruments so the workshop '
                    'itself plays a symphony before a single guitar string is ever plucked.'
                ),
                'cast_and_crew': (
                    'Director: Dominic Villamor\n'
                    'Featured Subjects: Tatay Celso Alegre, Maricel Alegre\n'
                    'Cinematographer: Dominic Villamor\n'
                    'Editor: Renz Cañete\n'
                    'Sound Designer: Lorenzo Alviola'
                ),
                'card_theme': 'theme-gold',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4',
                'screening_venue': 'Mactan Newtown Screening Room, Lapu-Lapu City',
                'screening_time': 'Sunday, 4:00 PM',
                'ticket_price': 150.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 1060,
            },
            {
                'creator': rafael_creator,
                'title': 'Dugo sa Parian',
                'native_title': 'Dugo sa Parian (Crimson of Parian)',
                'director': 'Rafael Ocampo',
                'institution': 'Mactan Celluloid',
                'category': 'SHORT',
                'runtime_minutes': 20,
                'logline': 'A stage actress confronts her estranged mentor on opening night.',
                'synopsis': (
                    'Behind the velvet curtains of a crumbling heritage theater in Parian, a lead actress preparing for '
                    'a Visayan tragedy receives an unexpected visit from the director who blacklisted her five years ago.'
                ),
                'director_note': (
                    'Staged as a chamber piece in one historic dressing room, the crimson palette mirrors the emotional '
                    'pressure cooker of live theater and artistic rivalry.'
                ),
                'cast_and_crew': (
                    'Director: Rafael Ocampo\n'
                    'Lead Cast: Celine Mercado, Victorio Ramos\n'
                    'Cinematographer: Antonette Lee\n'
                    'Editor: Tessa Magno\n'
                    'Sound Designer: Carlo Benedicto'
                ),
                'card_theme': 'theme-crimson',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4',
                'screening_venue': 'Teatro Sugbo, Colon Street, Cebu City',
                'screening_time': 'Friday, 8:30 PM',
                'ticket_price': 190.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 1510,
            },
            {
                'creator': bea_creator,
                'title': 'Anino sa Fuente',
                'native_title': 'Anino sa Fuente (Shadows at Fuente)',
                'director': 'Bea Carillo',
                'institution': 'Colon Street Frames',
                'category': 'SHORT',
                'runtime_minutes': 12,
                'logline': 'A street photographer develops a roll of film that shouldn’t exist.',
                'synopsis': (
                    'Working out of a tiny darkroom near Fuente Osmeña Circle, a street photographer develops an '
                    'unlabeled black-and-white roll left in a thrift-store camera—revealing candid portraits of his '
                    'own neighborhood from thirty years prior.'
                ),
                'director_note': (
                    'Shot on genuine monochrome digital sensors with vintage 1970s prime lenses, Anino sa Fuente '
                    'asks what memories a city stores in its concrete and shadows.'
                ),
                'cast_and_crew': (
                    'Director: Bea Carillo\n'
                    'Lead Cast: Emiliano Perez, Sofia Lim\n'
                    'Cinematographer: Jude Martinez\n'
                    'Editor: Camille Dizon\n'
                    'Sound Designer: Lorenzo Alviola'
                ),
                'card_theme': 'theme-noir',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4',
                'screening_venue': 'UP Cebu Performing Arts Hall, Gorordo Ave, Lahug',
                'screening_time': 'Sunday, 7:30 PM',
                'ticket_price': 150.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 1195,
            },
            {
                'creator': rafael_creator,
                'title': 'Lihim sa Bukid',
                'native_title': 'Lihim sa Bukid (Secret in the Highlands)',
                'director': 'Rafael Ocampo',
                'institution': 'University of San Jose-Recoletos (USJ-R)',
                'category': 'THESIS',
                'runtime_minutes': 24,
                'logline': 'A botany student documents endangered orchids in the fog of Busay.',
                'synopsis': (
                    'During a solo field expedition in the misty ridges of Busay and Balamban, a graduate botany '
                    'student befriends a reclusive herbalist who guards a valley of rare native orchids threatened by '
                    'a new mountain highway.'
                ),
                'director_note': (
                    'We hiked every dawn into the Cebu highlands with lightweight 16mm-emulation rigs to capture '
                    'the fleeting mountain fog before the sun burned it off.'
                ),
                'cast_and_crew': (
                    'Director: Rafael Ocampo\n'
                    'Lead Cast: Bianca Flores, Mang Eduardo Sotto\n'
                    'Cinematographer: Antonette Lee\n'
                    'Editor: Rafael Ocampo\n'
                    'Sound Designer: Nico Solis'
                ),
                'card_theme': 'theme-vintage',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
                'screening_venue': 'Robinsons Galleria Cebu Cinema Lounge',
                'screening_time': 'Saturday, 6:00 PM',
                'ticket_price': 130.00,
                'status': Film.STATUS_PUBLISHED,
                'views_count': 865,
            },
            {
                'creator': bea_creator,
                'title': 'Sugbo Nocturne',
                'native_title': 'Sugbo Nocturne (Workprint)',
                'director': 'Bea Carillo',
                'institution': 'Colon Street Frames',
                'category': 'SHORT',
                'runtime_minutes': 11,
                'logline': 'A late-night radio DJ answers calls from ferry passengers.',
                'synopsis': (
                    'Work-in-progress cut following an overnight FM host in Mandaue connecting callers aboard '
                    'inter-island ferries crossing the Camotes Sea.'
                ),
                'director_note': 'Early festival assembly cut prepared for Creator Studio review.',
                'cast_and_crew': (
                    'Director: Bea Carillo\n'
                    'Lead Cast: DJ Ramon Reyes\n'
                    'Cinematographer: Jude Martinez\n'
                    'Sound Designer: Lorenzo Alviola'
                ),
                'card_theme': 'theme-noir',
                'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoy.mp4',
                'screening_venue': 'TBA',
                'screening_time': 'TBA',
                'ticket_price': 140.00,
                'status': Film.STATUS_DRAFT,
                'views_count': 45,
            },
        ]

        created_films = {}
        count = 0
        for data in films_data:
            film, created = Film.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                count += 1
            else:
                for key, value in data.items():
                    setattr(film, key, value)
                film.save()
            created_films[film.title] = film

        # Seed sample tickets if none exist yet so Creator & Admin analytics are populated
        if Ticket.objects.count() == 0:
            sample_tickets = [
                (viewer_user, 'Mga Dalan sa Gabii', 3),
                (kyle_creator, 'Mga Dalan sa Gabii', 2),
                (viewer_user, 'Sinulog sa Kahilom', 2),
                (viewer_user, 'Asin ug Hangin', 4),
                (bea_creator, 'Ang Panaw', 3),
                (admin_user, 'Ang Panaw', 2),
                (viewer_user, 'Neon sa Mabolo', 2),
                (dominic_creator, 'Neon sa Mabolo', 1),
                (viewer_user, 'Karatula 1998', 2),
                (marisol_creator, 'Dugo sa Parian', 2),
                (rafael_creator, 'Mga Kamot sa Mactan', 3),
                (viewer_user, 'Anino sa Fuente', 1),
            ]
            for user_obj, film_title, seats in sample_tickets:
                if film_title in created_films:
                    Ticket.objects.create(user=user_obj, film=created_films[film_title], seats=seats)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(films_data)} films ({count} new), 7 accounts (5 creators), and {Ticket.objects.count()} tickets."
        ))
