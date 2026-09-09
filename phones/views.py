from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from categories.models import Category

from .forms import CartAddForm, PhoneForm
from .models import Order, OrderItem, Phone


CART_SESSION_KEY = "phone_store_cart"


def staff_required(view):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff)(view)


def home(request: HttpRequest) -> HttpResponse:
    phones = Phone.objects.select_related("category").prefetch_related("features")
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    brand = request.GET.get("brand", "").strip()
    availability = request.GET.get("availability", "").strip()
    sort = request.GET.get("sort", "newest").strip()

    if query:
        phones = phones.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(model__icontains=query)
        )
    if category_id.isdigit():
        phones = phones.filter(category_id=category_id)
    if brand:
        phones = phones.filter(brand__icontains=brand)
    if availability == "available":
        phones = phones.filter(is_available=True, stock__gt=0)
    elif availability == "unavailable":
        phones = phones.filter(Q(is_available=False) | Q(stock=0))

    sort_fields = {
        "price_low": "price",
        "price_high": "-price",
        "name": "name",
        "newest": "-created_at",
    }
    phones = phones.order_by(sort_fields.get(sort, "-created_at"))

    categories = Category.objects.all()
    brands = Phone.objects.order_by("brand").values_list("brand", flat=True).distinct()
    return render(
        request,
        "phones/home.html",
        {
            "phones": phones,
            "categories": categories,
            "brands": brands,
            "selected_category": category_id,
            "selected_brand": brand,
            "selected_availability": availability,
            "selected_sort": sort,
            "query": query,
            "cart_count": _cart_count(request),
        },
    )


def phone_detail(request: HttpRequest, pk: int) -> HttpResponse:
    phone = get_object_or_404(
        Phone.objects.select_related("category").prefetch_related("features"), pk=pk
    )
    return render(request, "phones/detail.html", {"phone": phone, "cart_add_form": CartAddForm()})


@staff_required
def phone_create(request: HttpRequest) -> HttpResponse:
    form = PhoneForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        phone = form.save()
        messages.success(request, f"تمت إضافة {phone.name} بنجاح.")
        return redirect("phone_detail", pk=phone.pk)
    return render(request, "phones/phone_form.html", {"form": form, "form_title": "إضافة جوال جديد"})


@staff_required
def phone_update(request: HttpRequest, pk: int) -> HttpResponse:
    phone = get_object_or_404(Phone, pk=pk)
    form = PhoneForm(request.POST or None, request.FILES or None, instance=phone)
    if request.method == "POST" and form.is_valid():
        phone = form.save()
        messages.success(request, f"تم تحديث {phone.name} بنجاح.")
        return redirect("phone_detail", pk=phone.pk)
    return render(request, "phones/phone_form.html", {"form": form, "form_title": "تعديل بيانات الجوال"})


@staff_required
def phone_delete(request: HttpRequest, pk: int) -> HttpResponse:
    phone = get_object_or_404(Phone, pk=pk)
    if request.method == "POST":
        name = phone.name
        phone.delete()
        messages.success(request, f"تم حذف {name}.")
        return redirect("home")
    return render(request, "phones/phone_confirm_delete.html", {"phone": phone})


def queryset_demo(request: HttpRequest) -> HttpResponse:
    all_phones = Phone.objects.all()
    available_phones = Phone.objects.filter(is_available=True, stock__gt=0)
    valid_phones = Phone.objects.exclude(price=0)
    sorted_phones = Phone.objects.order_by("-price")
    phone_values = Phone.objects.values("name", "brand", "price")
    available_count = available_phones.count()
    has_stock = Phone.objects.filter(stock__gt=0).exists()
    return render(
        request,
        "phones/queryset_demo.html",
        {
            "all_phones": all_phones,
            "available_phones": available_phones,
            "valid_phones": valid_phones,
            "sorted_phones": sorted_phones,
            "phone_values": phone_values,
            "available_count": available_count,
            "has_stock": has_stock,
        },
    )


def _get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def _cart_count(request):
    return sum(_get_cart(request).values())


def _cart_lines(request):
    cart = _get_cart(request)
    phones = Phone.objects.filter(pk__in=cart.keys()).select_related("category")
    lines = []
    total = Decimal("0.00")
    for phone in phones:
        quantity = int(cart.get(str(phone.pk), 0))
        if quantity <= 0:
            continue
        subtotal = phone.price * quantity
        total += subtotal
        lines.append({"phone": phone, "quantity": quantity, "subtotal": subtotal})
    return lines, total


def cart_add(request: HttpRequest, pk: int) -> HttpResponse:
    phone = get_object_or_404(Phone, pk=pk)
    form = CartAddForm(request.POST or None)
    if request.method != "POST" or not form.is_valid():
        messages.error(request, "تعذر إضافة المنتج. تحقق من الكمية.")
        return redirect("phone_detail", pk=pk)
    quantity = form.cleaned_data["quantity"]
    if not phone.in_stock:
        messages.error(request, "هذا الجوال غير متوفر حاليًا.")
        return redirect("phone_detail", pk=pk)
    cart = _get_cart(request).copy()
    new_quantity = int(cart.get(str(pk), 0)) + quantity
    if new_quantity > phone.stock:
        messages.error(request, f"الكمية المتاحة حاليًا هي {phone.stock} فقط.")
        return redirect("phone_detail", pk=pk)
    cart[str(pk)] = new_quantity
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True
    messages.success(request, "تمت إضافة الجوال إلى السلة.")
    return redirect("cart_detail")


def cart_detail(request: HttpRequest) -> HttpResponse:
    lines, total = _cart_lines(request)
    return render(request, "phones/cart.html", {"lines": lines, "total": total, "cart_count": _cart_count(request)})


def cart_update(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        cart = _get_cart(request).copy()
        for key in list(cart):
            value = request.POST.get(f"quantity_{key}", "0")
            try:
                quantity = max(0, int(value))
            except ValueError:
                quantity = 0
            phone = Phone.objects.filter(pk=key).first()
            if not phone or quantity == 0:
                cart.pop(key, None)
            else:
                cart[key] = min(quantity, phone.stock)
        request.session[CART_SESSION_KEY] = cart
        request.session.modified = True
        messages.success(request, "تم تحديث السلة.")
    return redirect("cart_detail")


def cart_remove(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        cart = _get_cart(request).copy()
        cart.pop(str(pk), None)
        request.session[CART_SESSION_KEY] = cart
        request.session.modified = True
        messages.success(request, "تم حذف المنتج من السلة.")
    return redirect("cart_detail")


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return redirect("cart_detail")
    cart = _get_cart(request)
    if not cart:
        messages.error(request, "السلة فارغة.")
        return redirect("cart_detail")

    with transaction.atomic():
        phones = {
            str(phone.pk): phone
            for phone in Phone.objects.select_for_update().filter(pk__in=cart.keys())
        }
        items = []
        total = Decimal("0.00")
        for key, raw_quantity in cart.items():
            phone = phones.get(str(key))
            quantity = int(raw_quantity)
            if not phone or not phone.in_stock or quantity > phone.stock:
                messages.error(request, "تغير المخزون، راجع السلة ثم حاول مرة أخرى.")
                return redirect("cart_detail")
            items.append((phone, quantity))
            total += phone.price * quantity

        order = Order.objects.create(user=request.user, total=total)
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    phone=phone,
                    phone_name=phone.name,
                    price=phone.price,
                    quantity=quantity,
                )
                for phone, quantity in items
            ]
        )
        for phone, quantity in items:
            phone.stock -= quantity
            if phone.stock == 0:
                phone.is_available = False
            phone.save(update_fields=["stock", "is_available", "updated_at"])

    request.session.pop(CART_SESSION_KEY, None)
    messages.success(request, "تم إنشاء طلبك بنجاح.")
    return redirect("order_detail", pk=order.pk)


@login_required
def order_list(request: HttpRequest) -> HttpResponse:
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "phones/order_list.html", {"orders": orders})


@login_required
def order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    queryset = Order.objects.prefetch_related("items")
    if request.user.is_staff:
        order = get_object_or_404(queryset, pk=pk)
    else:
        order = get_object_or_404(queryset, pk=pk, user=request.user)
    return render(request, "phones/order_detail.html", {"order": order})
