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
