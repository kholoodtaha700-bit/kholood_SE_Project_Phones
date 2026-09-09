from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم التصنيف")
    icon = models.CharField(
        max_length=50,
        default="bi-phone",
        verbose_name="الأيقونة",
        help_text="اسم أيقونة Bootstrap مثل bi-phone أو bi-apple",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name
