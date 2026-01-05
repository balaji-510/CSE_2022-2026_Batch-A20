from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core.mail import send_mail
import random
from django.contrib.auth.models import User as DjangoUser

from .models import EmailOTP


# ---------------- BASIC PAGES ----------------

def home(request):
    return render(request, 'core/home.html')


def login_page(request):
    return render(request, 'core/login.html')


def signup_page(request):
    return render(request, 'core/signup.html')


def role_selection(request):
    return render(request, 'core/role_selection.html')


def details_form(request):
    return render(request, 'core/details_form.html')


# ---------------- OTP LOGIC ----------------

def generate_and_send_otp(email, force_resend=False):
    """
    Generates OTP only if:
    - No existing OTP, OR
    - force_resend=True
    """

    existing = EmailOTP.objects.filter(email=email).first()

    if existing and not force_resend:
        otp = existing.otp_code
    else:
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.filter(email=email).delete()
        EmailOTP.objects.create(email=email, otp_code=otp)

    send_mail(
        subject='CodeNest Email Verification',
        message=f'Your CodeNest verification code is {otp}',
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )


def send_otp_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        generate_and_send_otp(email)
        return JsonResponse({'message': 'OTP sent'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def resend_otp_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        generate_and_send_otp(email, force_resend=True)
        return JsonResponse({'message': 'OTP resent'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def verify_otp_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        otp = request.POST.get('otp')

        try:
            otp_obj = EmailOTP.objects.get(email=email, otp_code=otp)

            if otp_obj.is_expired():
                return JsonResponse({'error': 'OTP expired'})

            otp_obj.delete()
            return JsonResponse({'message': 'Email verified'})

        except EmailOTP.DoesNotExist:
            return JsonResponse({'error': 'Invalid OTP'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

import json
from django.views.decorators.csrf import csrf_exempt
from .models import User, CodingPlatform
from django.contrib.auth.hashers import make_password

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = json.loads(request.body)

        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")
        platforms = data.get("platforms", [])

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "User already exists"})

        user = User.objects.create(
            full_name=full_name,
            email=email,
            role=role,
            password=make_password(password),
            email_verified=True
        )

        if role == "student":
            for url in platforms:
                CodingPlatform.objects.create(
                    user=user,
                    platform_name="Other",
                    profile_url=url
                )
        # create django auth user
        DjangoUser.objects.create_user(
            username=email,
            email=email,
            password=password
        )


        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid request"}, status=400)

from django.contrib.auth.decorators import login_required

@login_required(login_url="/login/")
def student_dashboard(request):
    return render(request, "core/student_dashboard.html")

@login_required(login_url="/login/")
def faculty_dashboard(request):
    return render(request, "core/faculty_dashboard.html")




from django.contrib.auth.hashers import check_password

from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import User


from django.contrib.auth import authenticate, login

def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

        if user is None:
            return JsonResponse({"error": "Invalid credentials"})

        login(request, user)  # 🔥 THIS CREATES REAL SESSION

        # get role from your custom User table
        custom_user = User.objects.get(email=email)

        return JsonResponse({
            "status": "success",
            "role": custom_user.role
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


