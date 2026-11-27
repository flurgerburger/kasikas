from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Film, Ticket


class AuthPagesTests(TestCase):
    def test_login_page_renders_with_password_toggle(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-target="id_password"')
        self.assertContains(response, 'password-toggle-btn')
        self.assertContains(response, 'password-toggle.js')

    def test_register_page_renders_with_password_toggles(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-target="id_password1"')
        self.assertContains(response, 'data-target="id_password2"')
        self.assertContains(response, 'password-toggle.js')


class CinemaAndStreamingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cebu_cinephile', password='Password123!')
        self.film = Film.objects.create(
            title='Mga Dalan sa Gabii',
            native_title='Mga Dalan sa Gabii (Streets of the Night)',
            director='Bea Carillo',
            institution='UP Cebu',
            category='SHORT',
            runtime_minutes=14,
            logline='A quiet walk through the city after the last jeepney.',
            synopsis='A reflective slow-cinema walk through Colon Street after midnight.',
            cast_and_crew='Director: Bea Carillo\nCinematography: Jude Martinez',
            card_theme='card-coral',
            video_url='https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
            screening_venue='Cinema Sugbo, Mango Square, Cebu City',
            screening_time='Friday, 7:30 PM',
            ticket_price=150.00
        )

    def test_home_page_displays_catalog(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mga Dalan sa Gabii')
        self.assertContains(response, 'SHORT FILM / 14 MIN')
        self.assertContains(response, reverse('film_detail', args=[self.film.id]))

    def test_film_detail_page_renders_details_and_ctas(self):
        response = self.client.get(reverse('film_detail', args=[self.film.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mga Dalan sa Gabii')
        self.assertContains(response, 'Bea Carillo')
        self.assertContains(response, 'Cinema Sugbo, Mango Square, Cebu City')
        self.assertContains(response, 'Stream Now')

    def test_watch_page_requires_login(self):
        response = self.client.get(reverse('watch_film', args=[self.film.id]))
        self.assertEqual(response.status_code, 302)

    def test_watch_page_renders_video_element_for_logged_in_user(self):
        self.client.login(username='cebu_cinephile', password='Password123!')
        response = self.client.get(reverse('watch_film', args=[self.film.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<video')
        self.assertContains(response, 'id="kasikas-player"')
        self.assertContains(response, self.film.video_url)

    def test_book_ticket_flow_and_my_tickets_rendering(self):
        self.client.login(username='cebu_cinephile', password='Password123!')
        
        # Book a ticket
        post_response = self.client.post(
            reverse('book_ticket', args=[self.film.id]),
            {'seats': 2}
        )
        self.assertRedirects(post_response, reverse('my_tickets'))
        
        # Verify ticket creation in DB
        self.assertEqual(Ticket.objects.filter(user=self.user, film=self.film).count(), 1)
        ticket = Ticket.objects.get(user=self.user, film=self.film)
        self.assertEqual(ticket.seats, 2)

        # Check My Tickets page
        tickets_response = self.client.get(reverse('my_tickets'))
        self.assertEqual(tickets_response.status_code, 200)
        self.assertContains(tickets_response, 'Mga Dalan sa Gabii')
        self.assertContains(tickets_response, 'Cinema Sugbo')
        self.assertContains(tickets_response, '2 Passes')
        self.assertContains(tickets_response, str(ticket.ticket_code)[:8].upper())
        self.assertContains(tickets_response, 'data-code="KASIKAS-PASS:')


from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserProfile


class RoleRoutingAndDashboardsTests(TestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(username='viewer_user', password='Password123!')
        UserProfile.objects.create(user=self.viewer, role=UserProfile.ROLE_VIEWER)

        self.creator = User.objects.create_user(username='creator_user', password='Password123!')
        UserProfile.objects.create(user=self.creator, role=UserProfile.ROLE_CREATOR)

        self.admin_user = User.objects.create_user(
            username='platform_admin',
            password='Password123!',
            is_staff=True,
            is_superuser=True,
        )
        UserProfile.objects.create(user=self.admin_user, role=UserProfile.ROLE_ADMIN)

        self.published_film = Film.objects.create(
            creator=self.creator,
            title='Published Short',
            director='Creator User',
            category='SHORT',
            runtime_minutes=12,
            logline='A published indie short.',
            synopsis='Full synopsis for published short.',
            ticket_price=150.00,
            status=Film.STATUS_PUBLISHED,
            views_count=100,
        )
        self.draft_film = Film.objects.create(
            creator=self.creator,
            title='Secret Draft Short',
            director='Creator User',
            category='SHORT',
            runtime_minutes=10,
            logline='A draft indie short.',
            synopsis='Full synopsis for draft short.',
            ticket_price=120.00,
            status=Film.STATUS_DRAFT,
            views_count=5,
        )
        Ticket.objects.create(user=self.viewer, film=self.published_film, seats=2)

    def test_regular_login_and_register_hide_admin_role(self):
        login_resp = self.client.get(reverse('login'))
        self.assertContains(login_resp, 'value="VIEWER"')
        self.assertContains(login_resp, 'value="CREATOR"')
        self.assertNotContains(login_resp, 'value="ADMIN"')

        reg_resp = self.client.get(reverse('register'))
        self.assertContains(reg_resp, 'value="VIEWER"')
        self.assertContains(reg_resp, 'value="CREATOR"')
        self.assertNotContains(reg_resp, 'value="ADMIN"')

    def test_login_as_viewer_routes_to_home(self):
        resp = self.client.post(reverse('login'), {
            'username': 'viewer_user',
            'password': 'Password123!',
            'role': 'VIEWER',
        })
        self.assertRedirects(resp, reverse('home'))
        self.assertEqual(self.client.session.get('active_role'), UserProfile.ROLE_VIEWER)

    def test_login_as_creator_routes_to_creator_dashboard_and_allows_viewer_browsing(self):
        resp = self.client.post(reverse('login'), {
            'username': 'viewer_user',
            'password': 'Password123!',
            'role': 'CREATOR',
        })
        self.assertRedirects(resp, reverse('creator_dashboard'))
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.profile.role, UserProfile.ROLE_CREATOR)
        self.assertEqual(self.client.session.get('active_role'), UserProfile.ROLE_CREATOR)

        # Creator can still browse Viewer screens
        home_resp = self.client.get(reverse('home'))
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, 'Creator Studio')

    def test_register_as_creator_routes_to_creator_dashboard(self):
        resp = self.client.post(reverse('register'), {
            'username': 'new_filmmaker',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'role': 'CREATOR',
        })
        self.assertRedirects(resp, reverse('creator_dashboard'))
        new_user = User.objects.get(username='new_filmmaker')
        self.assertEqual(new_user.profile.role, UserProfile.ROLE_CREATOR)

    def test_admin_login_routing_and_access_control(self):
        # Non-admin rejected on /admin-login/
        non_admin_resp = self.client.post(reverse('admin_login'), {
            'username': 'viewer_user',
            'password': 'Password123!',
        })
        self.assertEqual(non_admin_resp.status_code, 200)
        self.assertContains(non_admin_resp, 'Access denied')

        # Admin on regular /login/ auto-routes to admin_dashboard
        admin_resp = self.client.post(reverse('login'), {
            'username': 'platform_admin',
            'password': 'Password123!',
            'role': 'VIEWER',
        })
        self.assertRedirects(admin_resp, reverse('admin_dashboard'))

        # Admin dashboard renders overview, table, and charts
        dash_resp = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, 'Platform')
        self.assertContains(dash_resp, 'Published Short')
        self.assertContains(dash_resp, '₱300.00')
        self.assertContains(dash_resp, 'Movie Performance Table')

    def test_viewer_cannot_access_creator_or_admin_dashboards(self):
        self.client.login(username='viewer_user', password='Password123!')
        self.assertRedirects(self.client.get(reverse('creator_dashboard')), reverse('home'))
        self.assertRedirects(self.client.get(reverse('admin_dashboard')), reverse('home'))

    def test_creator_dashboard_upload_and_status_toggle(self):
        self.client.login(username='creator_user', password='Password123!')
        session = self.client.session
        session['active_role'] = UserProfile.ROLE_CREATOR
        session.save()

        dash_resp = self.client.get(reverse('creator_dashboard'))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, 'Published Short')
        self.assertContains(dash_resp, 'Secret Draft Short')
        self.assertContains(dash_resp, '₱300.00')

        # Upload a new short movie
        video_mock = SimpleUploadedFile('short.mp4', b'fake-mp4-data', content_type='video/mp4')
        thumb_mock = SimpleUploadedFile('poster.png', b'fake-png-data', content_type='image/png')
        upload_resp = self.client.post(reverse('creator_dashboard'), {
            'title': 'Baybayon',
            'director': 'Creator User',
            'category': 'SHORT',
            'runtime_minutes': 16,
            'logline': 'Dawn by the pier.',
            'synopsis': 'A fisherman waits for the morning tide.',
            'card_theme': 'card-green',
            'ticket_price': '200.00',
            'status': Film.STATUS_PUBLISHED,
            'screening_venue': 'Cinema Sugbo',
            'screening_time': 'Friday, 7:00 PM',
            'video_file': video_mock,
            'thumbnail_file': thumb_mock,
        })
        self.assertRedirects(upload_resp, reverse('creator_dashboard'))
        new_film = Film.objects.get(title='Baybayon')
        self.assertEqual(new_film.creator, self.creator)
        self.assertEqual(new_film.ticket_price, 200)

        # Draft film hidden from public home, published visible
        home_resp = self.client.get(reverse('home'))
        self.assertContains(home_resp, 'Baybayon')
        self.assertNotContains(home_resp, 'Secret Draft Short')

        # Toggle draft film to published
        toggle_resp = self.client.post(reverse('toggle_film_status', args=[self.draft_film.id]))
        self.assertRedirects(toggle_resp, reverse('creator_dashboard'))
        self.draft_film.refresh_from_db()
        self.assertEqual(self.draft_film.status, Film.STATUS_PUBLISHED)

    def test_watch_film_increments_views_count(self):
        self.client.login(username='viewer_user', password='Password123!')
        before = self.published_film.views_count
        self.client.get(reverse('watch_film', args=[self.published_film.id]))
        self.published_film.refresh_from_db()
        self.assertEqual(self.published_film.views_count, before + 1)


class ReelCarouselAndCatalogTests(TestCase):
    def test_seed_films_populates_expanded_catalog_and_themes(self):
        from django.core.management import call_command

        call_command('seed_films')
        published = Film.objects.filter(status=Film.STATUS_PUBLISHED)
        self.assertGreaterEqual(published.count(), 12)

        distinct_themes = set(published.values_list('card_theme', flat=True))
        self.assertGreaterEqual(len(distinct_themes), 6)

        home_resp = self.client.get(reverse('home'))
        self.assertEqual(home_resp.status_code, 200)
        self.assertContains(home_resp, 'reel-carousel-track')
        self.assertContains(home_resp, 'reel-prev-btn')
        self.assertContains(home_resp, 'reel-next-btn')
        self.assertContains(home_resp, 'reel-carousel.js')
        self.assertContains(home_resp, '12 local works')

        sample_film = published.get(title='Neon sa Mabolo')
        detail_resp = self.client.get(reverse('film_detail', args=[sample_film.id]))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "Director's Note")
        self.assertContains(detail_resp, 'Cast &amp; Crew')
        self.assertContains(detail_resp, 'NEON CYBERPUNK')
        self.assertContains(detail_resp, 'Kenji Velasco')


class ProfileEditAndBrowseTests(TestCase):
    def setUp(self):
        self.viewer = User.objects.create_user(username='profile_viewer', password='Password123!')
        UserProfile.objects.create(user=self.viewer, role=UserProfile.ROLE_VIEWER)

        self.creator = User.objects.create_user(username='profile_creator', password='Password123!')
        UserProfile.objects.create(
            user=self.creator,
            role=UserProfile.ROLE_CREATOR,
            studio_name='Sugbo Indie Collective',
        )

        self.other_creator = User.objects.create_user(username='other_creator', password='Password123!')
        UserProfile.objects.create(user=self.other_creator, role=UserProfile.ROLE_CREATOR)

        self.film1 = Film.objects.create(
            creator=self.creator,
            title='Dagat sa Kabuntagon',
            native_title='Sea at Dawn',
            director='Bea Carillo',
            institution='UP Cebu',
            category='SHORT',
            runtime_minutes=14,
            logline='Fishermen at dawn.',
            synopsis='A quiet look at Cebu coastal fishermen.',
            director_note='Shot on location in Cordova.',
            screening_venue='Cinema Sugbo, Cebu City',
            ticket_price=150.00,
            status=Film.STATUS_PUBLISHED,
        )
        self.film2 = Film.objects.create(
            creator=self.creator,
            title='Bukid Chronicles',
            director='Kyle Navarro',
            institution='USC Talamban',
            category='DOCU',
            runtime_minutes=25,
            logline='Mountain barangay life.',
            synopsis='Documentary on highland farmers.',
            screening_venue='UP Cebu Performing Arts Hall',
            ticket_price=120.00,
            status=Film.STATUS_PUBLISHED,
        )
        Ticket.objects.create(user=self.viewer, film=self.film1, seats=3)

    def test_profile_page_displays_identity_stats_and_updates_fields(self):
        self.client.login(username='profile_viewer', password='Password123!')
        resp = self.client.get(reverse('profile'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '@profile_viewer')
        self.assertContains(resp, '3')
        self.assertContains(resp, 'Switch to Indie Creator Mode')

        # Update profile details
        post_resp = self.client.post(reverse('profile'), {
            'action': 'update_profile',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'email': 'maria@kasikas.ph',
            'studio_name': 'Sugbo Indie Collective',
            'bio': 'Cebuano filmmaker and cinephile.',
        })
        self.assertRedirects(post_resp, reverse('profile'))
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.first_name, 'Maria')
        self.assertEqual(self.viewer.email, 'maria@kasikas.ph')
        self.assertEqual(self.viewer.profile.studio_name, 'Sugbo Indie Collective')

    def test_profile_instant_role_switcher_toggles_viewer_and_creator(self):
        self.client.login(username='profile_viewer', password='Password123!')
        resp = self.client.post(reverse('profile'), {'action': 'switch_role'})
        self.assertRedirects(resp, reverse('profile'))
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.profile.role, UserProfile.ROLE_CREATOR)
        self.assertEqual(self.client.session.get('active_role'), UserProfile.ROLE_CREATOR)

        # Toggle back to Viewer
        resp2 = self.client.post(reverse('profile'), {'action': 'switch_role'})
        self.assertRedirects(resp2, reverse('profile'))
        self.viewer.refresh_from_db()
        self.assertEqual(self.viewer.profile.role, UserProfile.ROLE_VIEWER)
        self.assertEqual(self.client.session.get('active_role'), UserProfile.ROLE_VIEWER)

    def test_edit_and_delete_film_permissions_and_crud(self):
        # Other creator cannot edit
        self.client.login(username='other_creator', password='Password123!')
        forbidden_resp = self.client.get(reverse('edit_film', args=[self.film1.id]))
        self.assertRedirects(forbidden_resp, reverse('creator_dashboard'))

        # Owner creator can edit
        self.client.login(username='profile_creator', password='Password123!')
        edit_get = self.client.get(reverse('edit_film', args=[self.film1.id]))
        self.assertEqual(edit_get.status_code, 200)
        self.assertContains(edit_get, 'Dagat sa Kabuntagon')

        edit_post = self.client.post(reverse('edit_film', args=[self.film1.id]), {
            'title': 'Dagat sa Kabuntagon (Director Cut)',
            'director': 'Bea Carillo',
            'category': 'SHORT',
            'runtime_minutes': 16,
            'logline': 'Updated logline.',
            'synopsis': 'Updated synopsis.',
            'director_note': 'Updated festival note.',
            'card_theme': 'theme-gold',
            'screening_venue': 'Cinema Sugbo, Cebu City',
            'screening_time': 'Saturday, 8:00 PM',
            'ticket_price': '175.00',
            'status': Film.STATUS_PUBLISHED,
        })
        self.assertRedirects(edit_post, reverse('creator_dashboard'))
        self.film1.refresh_from_db()
        self.assertEqual(self.film1.title, 'Dagat sa Kabuntagon (Director Cut)')
        self.assertEqual(self.film1.director_note, 'Updated festival note.')
        self.assertEqual(self.film1.ticket_price, 175)

        # Owner creator can delete
        del_post = self.client.post(reverse('edit_film', args=[self.film1.id]), {'action': 'delete'})
        self.assertRedirects(del_post, reverse('creator_dashboard'))
        self.assertFalse(Film.objects.filter(pk=self.film1.id).exists())

    def test_browse_search_and_filters(self):
        # Search by studio name / title
        resp_q = self.client.get(reverse('browse'), {'q': 'Cordova'})
        self.assertEqual(resp_q.status_code, 200)
        self.assertContains(resp_q, 'Dagat sa Kabuntagon')
        self.assertNotContains(resp_q, 'Bukid Chronicles')

        # Filter by category
        resp_cat = self.client.get(reverse('browse'), {'category': 'DOCU'})
        self.assertContains(resp_cat, 'Bukid Chronicles')
        self.assertNotContains(resp_cat, 'Dagat sa Kabuntagon')

        # Filter by institution
        resp_inst = self.client.get(reverse('browse'), {'institution': 'UP Cebu'})
        self.assertContains(resp_inst, 'Dagat sa Kabuntagon')
        self.assertNotContains(resp_inst, 'Bukid Chronicles')

        # Filter by venue
        resp_venue = self.client.get(reverse('browse'), {'venue': 'UP Cebu Performing Arts Hall'})
        self.assertContains(resp_venue, 'Bukid Chronicles')
        self.assertNotContains(resp_venue, 'Dagat sa Kabuntagon')
