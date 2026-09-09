# التقرير النهائي — PhoneStore Lab 6/7

## أ. حالة المشروع قبل التعديل

المشروع تطبيق Django قائم باسم `MobilePhonesStore` ويضم تطبيقات `phones` و`categories` و`accounts`. كانت فيه مصادقة باستخدام Django، كتالوج جوالات مرتبط بقاعدة البيانات، بحث وتصفية وترتيب، تصنيفات، صور منتجات عبر `ImageField`، سلة تعتمد على الجلسة، إنشاء طلبات، وصلاحيات `staff` لإدارة المنتجات والتصنيفات. كما كانت إعدادات `STATIC` و`MEDIA` ومسارات خدمة الوسائط في وضع التطوير موجودة مسبقًا.

## ب. ما تم تطبيقه من مفاهيم المحاضرة

تم الحفاظ على المصادقة الموجودة وتطويرها بدل استبدالها. أضيفت Middleware خفيفة باسم `RequestTimingMiddleware` تمر بعد `AuthenticationMiddleware` وتضيف ترويسة `X-Request-Duration-ms` لقياس زمن الاستجابة دون تغيير منطق الطلبات. كما تم تجهيز إعدادات البريد القابلة للتبديل بين Console في التطوير وSMTP عبر متغيرات البيئة، مع إبقاء الأسرار خارج الكود.

## ج. تنفيذ التكليف

المستخدم المسجل دخوله يُعاد توجيهه من `/login/` و`/register/` إلى الصفحة الرئيسية مع رسالة مناسبة. المستخدم غير المسجل يستطيع الوصول إلى الصفحتين، بينما يبقى Logout والمنتجات والتفاصيل والبحث والتصنيفات والسلة والإدارة محمية أو متاحة وفق قواعد المشروع الأصلية. يظهر اسم المستخدم وحالته في شريط التنقل، وتظهر روابط Login/Register فقط للزائر.

## د. ثيم Django Admin

تم اختيار **Jazzmin** لأنه Drop-in theme مناسب لتطبيق Django Admin الحالي، ولا يتطلب تغيير تسجيلات `ModelAdmin` أو نماذج المشروع. تمت إضافته إلى `requirements.txt` وإلى `INSTALLED_APPS` قبل `django.contrib.admin`، مع إعداد هوية PhoneStore وشريط تنقل واضح وواجهة فاتحة منظمة. إصدار Django الفعلي المستخدم في التحقق هو **5.2.17**.

## هـ. المصادقة

تمت إضافة فحص `request.user.is_authenticated` في Views الدخول والتسجيل. عند محاولة المستخدم المسجل فتح أي منهما يدويًا، تتم إعادة توجيهه إلى `home`. بقيت آلية `AuthenticationForm` و`UserCreationForm` وتدفق التسجيل وتسجيل الخروج كما هي، مع الحفاظ على CSRF ورسائل Django.

## و. Media وStatic

تم الحفاظ على `MEDIA_URL=/media/` و`MEDIA_ROOT=BASE_DIR / "media"`، ومسار `STATIC_URL=/static/` و`STATIC_ROOT`. صور الجوالات الحالية بقيت في `media/phones/`، وتستمر القوالب في استخدام `phone.image.url` مع fallback أيقونة عند غياب الصورة. تم التحقق فعليًا من استجابة صورة عبر `/media/phones/1.jpg`.

## ز. البريد والتواصل

أضيفت صفحة `/contact/` مرتبطة بنموذج بسيط وآمن، وتستخدم `EmailMessage` مع قالب نصي، و`reply_to` لبريد المستخدم. كل الرسائل موجهة إلى `engreemalwaeel@gmail.com`. يستخدم التطوير `console.EmailBackend` افتراضيًا، ويمكن تفعيل SMTP عبر `EMAIL_HOST` و`EMAIL_PORT` و`EMAIL_HOST_USER` و`EMAIL_HOST_PASSWORD` و`EMAIL_USE_TLS` في `.env`، دون وضع كلمات المرور داخل الكود.

## ح. تحسين الواجهة

تم توحيد التصميم في CSS باستخدام Arial، وRTL، وتدرجات فاتحة ومساحات بيضاء وبطاقات متناسقة وصور `object-fit: contain` واستجابة للشاشات الصغيرة. تم اعتماد نظام ألوان:

| الدور | اللون |
|---|---|
| Primary | `#4F46E5` |
| Primary Dark | `#3730A3` |
| Secondary | `#0F766E` |
| Accent | `#F59E0B` |
| Background | `#F7F8FC` |
| Surface | `#FFFFFF` |
| Text | `#172033` |
| Muted Text | `#6B7280` |
| Border | `#E6E9F1` |
| Success | `#16805D` |
| Danger | `#C2414B` |

تمت إضافة رابط التواصل، وتحسين حالة المستخدم والرسائل والأزرار والبطاقات والنماذج، مع عدم تغيير منطق السلة والطلبات والبحث.

## ط. الملفات المعدلة والمنشأة

أهم الملفات المعدلة هي `phone_store/settings.py` و`accounts/views.py` و`accounts/urls.py` و`templates/base.html` و`static/css/style.css` و`requirements.txt` و`.env.example`. أضيف الملف `phone_store/middleware.py`، وقالبا `templates/accounts/contact.html` و`templates/accounts/contact_email.txt`.

## ي. الاختبارات

| الاختبار | النتيجة |
|---|---|
| `DJANGO_TEST_MODE=1 python manage.py check` | نجح، لا توجد مشكلات |
| `DJANGO_TEST_MODE=1 python manage.py makemigrations --check --dry-run` | نجح، لا توجد تغييرات معلقة |
| `DJANGO_TEST_MODE=1 python manage.py test` | نجح: 12 اختبارًا |
| تحقق تكاملي Login/Register للمستخدم المسجل | نجح: إعادة توجيه إلى Home |
| Logout للمستخدم المسجل | نجح |
| نموذج التواصل مع Local Email Backend | نجح، المستلم `engreemalwaeel@gmail.com` |
| خادم Django الفعلي | نجحت `/phones/` و`/login/` |
| Media | نجحت صورة `/media/phones/1.jpg` باستجابة HTTP 200 |

ملاحظة: التشغيل الافتراضي للمشروع يستخدم PostgreSQL كما كان محددًا أصلًا. تم إجراء التحقق المحلي المعزول باستخدام SQLite عبر `DJANGO_TEST_MODE=1`، ولم تُحذف قاعدة البيانات أو بياناتها.

## ك. التشغيل

```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

يجب استخدام `.env.example` كنقطة بداية وإنشاء `.env` محليًا، مع تعبئة بيانات PostgreSQL وSMTP عند الحاجة. لم يتم تضمين `.env` الأصلي في الحزمة النهائية حفاظًا على سرية بيانات الاتصال.
