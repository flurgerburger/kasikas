from django.test import TestCase
from django.urls import reverse


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
