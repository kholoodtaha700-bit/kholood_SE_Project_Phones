from django import forms

from categories.models import Category

from .models import Feature, Phone


class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = [
            "name",
            "brand",
            "model",
            "price",
            "description",
            "image",
            "stock",
            "is_available",
            "operating_system",
            "screen_size",
            "ram",
            "storage",
            "camera",
            "battery",
            "color",
            "category",
            "features",
        ]
        labels = {
            "name": "اسم الجوال",
            "brand": "الشركة",
            "model": "الموديل",
            "price": "السعر",
            "description": "الوصف",
            "image": "صورة الجوال",
            "stock": "المخزون",
            "is_available": "متاح للبيع",
            "operating_system": "نظام التشغيل",
            "screen_size": "حجم الشاشة بالبوصة",
            "ram": "الرام (GB)",
            "storage": "التخزين (GB)",
            "camera": "الكاميرا",
            "battery": "البطارية",
            "color": "اللون",
            "category": "التصنيف",
            "features": "المميزات",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "features": forms.CheckboxSelectMultiple,
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("يجب أن يكون السعر صفرًا أو أكبر.")
        return price

    def clean(self):
        cleaned_data = super().clean()
        stock = cleaned_data.get("stock")
        is_available = cleaned_data.get("is_available")
        if stock is not None and stock == 0 and is_available:
            self.add_error("is_available", "لا يمكن اعتبار الجوال متاحًا مع عدم وجود مخزون.")
        return cleaned_data


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100, initial=1)
