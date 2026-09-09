from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm
from .models import Category


def staff_required(view):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff)(view)


def category_list(request):
    categories = Category.objects.prefetch_related("phones")
    return render(request, "categories/category_list.html", {"categories": categories})


@staff_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"تمت إضافة التصنيف {category.name}.")
        return redirect("category_list")
    return render(request, "categories/category_form.html", {"form": form, "form_title": "إضافة تصنيف"})


@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"تم تحديث التصنيف {category.name}.")
        return redirect("category_list")
    return render(request, "categories/category_form.html", {"form": form, "form_title": "تعديل تصنيف"})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        name = category.name
        category.delete()
        messages.success(request, f"تم حذف التصنيف {name}.")
        return redirect("category_list")
    return render(request, "categories/category_confirm_delete.html", {"category": category})
