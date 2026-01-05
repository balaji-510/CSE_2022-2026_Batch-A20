from django.db import models
from django.utils import timezone
import uuid


# ------------------------
# USER MODEL
# ------------------------
class User(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    password = models.CharField(max_length=255)  # will hash later
    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# ------------------------
# EMAIL OTP MODEL
# ------------------------
class EmailOTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"{self.email} - {self.otp_code}"


# ------------------------
# CODING PLATFORM MODEL (STUDENT ONLY)
# ------------------------
class CodingPlatform(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='platforms')
    platform_name = models.CharField(max_length=50)
    profile_url = models.URLField()

    def __str__(self):
        return f"{self.platform_name} - {self.user.email}"
