from django.contrib import admin

from .models import Feature, Order, OrderItem, Phone, Warranty


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]
    search_fields = ["title"]


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "brand", "category", "price", "stock", "is_available"]
    list_filter = ["is_available", "category", "brand"]
    search_fields = ["name", "brand", "model"]
    filter_horizontal = ["features"]


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = ["phone", "duration_months", "provider"]
    search_fields = ["phone__name", "provider"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["phone_name", "price", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username"]
    inlines = [OrderItemInline]
