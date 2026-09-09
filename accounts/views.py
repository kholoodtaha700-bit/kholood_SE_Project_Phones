from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme


def register(request):
    if request.user.is_authenticated:
        messages.info(request, "أنت مسجل الدخول بالفعل.")
        return redirect("home")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "تم إنشاء حسابك بنجاح.")
        return redirect("home")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "أنت مسجل الدخول بالفعل.")
        return redirect("home")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "تم تسجيل الدخول بنجاح.")
        next_url = request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect("home")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.info(request, "تم تسجيل الخروج.")
    return redirect("home")


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("message", "").strip()
        if not all([name, email, subject, body]):
            messages.error(request, "يرجى تعبئة جميع الحقول.")
        else:
            content = render_to_string(
                "accounts/contact_email.txt",
                {"name": name, "email": email, "subject": subject, "body": body},
            )
            EmailMessage(
                subject=f"PhoneStore: {subject}",
                body=content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL],
                reply_to=[email],
            ).send(fail_silently=False)
            messages.success(request, "تم إرسال رسالتك بنجاح، وسنعاود التواصل معك قريبًا.")
            return redirect("contact")
    return render(request, "accounts/contact.html")
