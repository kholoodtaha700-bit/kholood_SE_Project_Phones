from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from categories.models import Category


class Feature(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="اسم الميزة")

    class Meta:
        ordering = ["title"]
        verbose_name = "ميزة"
        verbose_name_plural = "المميزات"

    def __str__(self):
        return self.title


class Phone(models.Model):
    name = models.CharField(max_length=150, verbose_name="اسم الجوال")
    brand = models.CharField(max_length=100, default="", verbose_name="الشركة")
    model = models.CharField(max_length=100, blank=True, verbose_name="الموديل")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="السعر",
    )
    description = models.TextField(blank=True, verbose_name="الوصف")
    image = models.ImageField(
        upload_to="phones/",
        blank=True,
        null=True,
        verbose_name="صورة الجوال",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="المخزون")
    is_available = models.BooleanField(default=True, verbose_name="متاح للبيع")
    operating_system = models.CharField(
        max_length=80, blank=True, verbose_name="نظام التشغيل"
    )
    screen_size = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name="حجم الشاشة بالبوصة",
    )
    ram = models.PositiveIntegerField(blank=True, null=True, verbose_name="الرام GB")
    storage = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="مساحة التخزين GB"
    )
    camera = models.CharField(max_length=100, blank=True, verbose_name="الكاميرا")
    battery = models.CharField(max_length=100, blank=True, verbose_name="البطارية")
    color = models.CharField(max_length=50, blank=True, verbose_name="اللون")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="phones",
        verbose_name="التصنيف",
    )
    features = models.ManyToManyField(
        Feature,
        blank=True,
        related_name="phones",
        verbose_name="المميزات",
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        ordering = ["-created_at", "name"]
        indexes = [
            models.Index(fields=["brand", "model"]),
            models.Index(fields=["category", "is_available"]),
        ]
        verbose_name = "جوال"
        verbose_name_plural = "الجوالات"

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.is_available and self.stock > 0


class Warranty(models.Model):
    phone = models.OneToOneField(
        Phone,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="warranty",
        verbose_name="الجوال",
    )
    duration_months = models.PositiveIntegerField(default=12, verbose_name="المدة بالشهور")
    provider = models.CharField(max_length=100, verbose_name="مزود الضمان")

    class Meta:
        verbose_name = "ضمان"
        verbose_name_plural = "الضمانات"

    def __str__(self):
        return f"ضمان {self.phone.name} - {self.duration_months} شهر"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "قيد المراجعة"
        CONFIRMED = "confirmed", "مؤكد"
        SHIPPED = "shipped", "تم الشحن"
        DELIVERED = "delivered", "تم التسليم"
        CANCELLED = "cancelled", "ملغي"

    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="orders", verbose_name="المستخدم"
    )
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="الإجمالي")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="الحالة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"

    def __str__(self):
        return f"طلب #{self.pk} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="الطلب"
    )
    phone = models.ForeignKey(
        Phone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="الجوال",
    )
    phone_name = models.CharField(max_length=150, verbose_name="اسم الجوال وقت الطلب")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلب"

    def __str__(self):
        return f"{self.phone_name} × {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
