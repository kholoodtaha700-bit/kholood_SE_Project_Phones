# Mobile Phones Store

مشروع متجر جوالات مبني باستخدام **Python وDjango وPostgreSQL وDjango Templates**. يدعم المشروع كتالوج الجوالات، التصنيفات، البحث والتصفية والترتيب، المصادقة، إدارة المنتجات والتصنيفات للمشرف، السلة، إنشاء الطلبات، ومتابعة الطلبات.

## التشغيل على Windows

أنشئ بيئة افتراضية ثم فعّلها:

```bash
python -m venv venv
venv\Scripts\activate
```

ثبّت المتطلبات:

```bash
pip install -r requirements.txt
```

انسخ `.env.example` إلى `.env`، ثم ضع بيانات قاعدة PostgreSQL الفعلية وقيمة عشوائية طويلة لـ `DJANGO_SECRET_KEY`. لا تضع كلمة المرور في ملفات Git أو في الكود.

أنشئ قاعدة البيانات `phone_store_db` في PostgreSQL، ثم نفّذ:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

بعدها افتح `http://127.0.0.1:8000/phones/`. تستخدم بيئة الاختبار الداخلية SQLite فقط عند تشغيل الأوامر مع `DJANGO_TEST_MODE=1`، ولا تمثل بديلًا دائمًا عن PostgreSQL.

## الاختبار

```bash
DJANGO_TEST_MODE=1 python manage.py check
DJANGO_TEST_MODE=1 python manage.py makemigrations --check --dry-run
DJANGO_TEST_MODE=1 python manage.py test
```

تتطلب عمليات إضافة وتعديل وحذف الجوالات والتصنيفات حسابًا بصلاحية staff. يمكن للزائر تصفح المتجر والبحث والتصفية وإضافة المنتجات إلى السلة، بينما يتطلب إتمام الطلب تسجيل الدخول.
