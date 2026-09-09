from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from categories.models import Category

from .forms import PhoneForm
from .models import Feature, Order, Phone


User = get_user_model()


class PhoneStoreTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="customer", password="StrongPass123!")
        self.staff = User.objects.create_user(
            username="manager", password="StrongPass123!", is_staff=True
        )
        self.category = Category.objects.create(name="Apple", icon="bi-apple")
        self.feature = Feature.objects.create(title="شحن سريع")
        self.phone = Phone.objects.create(
            name="iPhone 15",
            brand="Apple",
            model="15",
            price=Decimal("2999.00"),
            stock=4,
            category=self.category,
        )
        self.phone.features.add(self.feature)

    def test_phone_model_and_stock_property(self):
        self.assertEqual(str(self.phone), "iPhone 15")
        self.assertTrue(self.phone.in_stock)
        self.phone.stock = 0
        self.assertFalse(self.phone.in_stock)

    def test_phone_form_validates_zero_stock_availability(self):
        form = PhoneForm(
            data={
                "name": "Test Phone",
                "brand": "Test",
                "model": "X",
                "price": "100",
                "stock": "0",
                "is_available": "on",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("is_available", form.errors)

    def test_home_search_and_category_filter(self):
        response = self.client.get(reverse("home"), {"q": "iPhone", "category": self.category.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "iPhone 15")
        response = self.client.get(reverse("home"), {"q": "Samsung"})
        self.assertNotContains(response, "iPhone 15")

    def test_detail_and_url_resolution(self):
        response = self.client.get(reverse("phone_detail", args=[self.phone.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2999")

    def test_staff_only_phone_crud(self):
        response = self.client.get(reverse("add_phone"))
        self.assertEqual(response.status_code, 302)
        self.client.login(username="manager", password="StrongPass123!")
        response = self.client.post(
            reverse("add_phone"),
            {
                "name": "Galaxy S",
                "brand": "Samsung",
                "model": "S",
                "price": "2000",
                "stock": "2",
                "is_available": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Phone.objects.filter(name="Galaxy S").exists())

    def test_cart_and_checkout_create_order_and_decrement_stock(self):
        response = self.client.post(
            reverse("cart_add", args=[self.phone.pk]), {"quantity": 2}
        )
        self.assertRedirects(response, reverse("cart_detail"))
        self.client.login(username="customer", password="StrongPass123!")
        response = self.client.post(reverse("checkout"))
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse("order_detail", args=[order.pk]))
        self.phone.refresh_from_db()
        self.assertEqual(self.phone.stock, 2)
        self.assertEqual(order.total, Decimal("5998.00"))

    def test_order_detail_is_private_to_owner(self):
        order = Order.objects.create(user=self.user, total=Decimal("10.00"))
        self.client.login(username="manager", password="StrongPass123!")
        self.assertEqual(self.client.get(reverse("order_detail", args=[order.pk])).status_code, 200)
