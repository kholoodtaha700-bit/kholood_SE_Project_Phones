from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AccountTests(TestCase):
    def test_register_logs_user_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_login_and_logout(self):
        User.objects.create_user(username="member", password="StrongPass123!")
        self.assertTrue(self.client.login(username="member", password="StrongPass123!"))
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
