from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "icon"]
        labels = {"name": "اسم التصنيف", "icon": "أيقونة Bootstrap"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "مثال: Apple"}),
            "icon": forms.TextInput(attrs={"placeholder": "bi-apple"}),
        }
