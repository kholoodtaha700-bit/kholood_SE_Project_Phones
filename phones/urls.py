from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("queryset-demo/", views.queryset_demo, name="queryset_demo"),
    path("add/", views.phone_create, name="add_phone"),
    path("<int:pk>/", views.phone_detail, name="phone_detail"),
    path("<int:pk>/edit/", views.phone_update, name="phone_update"),
    path("<int:pk>/delete/", views.phone_delete, name="phone_delete"),
    path("<int:pk>/cart/add/", views.cart_add, name="cart_add"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/<int:pk>/remove/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
]
