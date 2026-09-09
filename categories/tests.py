from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category


User = get_user_model()


class CategoryTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Apple")
        self.staff = User.objects.create_user(
            username="manager", password="StrongPass123!", is_staff=True
        )

    def test_category_list_is_public(self):
        response = self.client.get(reverse("category_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apple")

    def test_category_create_requires_staff(self):
        self.assertEqual(self.client.get(reverse("category_add")).status_code, 302)
        self.client.login(username="manager", password="StrongPass123!")
        response = self.client.post(reverse("category_add"), {"name": "Samsung", "icon": "bi-phone"})
        self.assertRedirects(response, reverse("category_list"))
        self.assertTrue(Category.objects.filter(name="Samsung").exists())
