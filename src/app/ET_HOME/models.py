import uuid

import pyotp  # otp plugin for double auth (prototype now just an example)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

class User(AbstractUser):
    otp_secret = models.CharField(max_length=32, blank=True, null=True)     # double auth with otp
    otp_activated = models.BooleanField(default=False)

    def generate_otp_secret(self):
        self.otp_secret = pyotp.random_base32(length=32)
        self.save()

    def get_otp_uri(self):
        return pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.email,
            issuer_name="ET-HOME"
        )

    def verify_otp(self, otp):
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp, valid_window=1)


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_number = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    secret = models.CharField(max_length=128, null=True)
    secret_id = models.UUIDField(null=True)
    added_at = models.DateTimeField(auto_now_add=True)


class SpendingCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=False)
    is_default = models.BooleanField(default=False)
    user_budget = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    trigger_notification = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "user")

    def __str__(self):
        return f"{self.name} - {self.user.username if self.user else 'No User'}"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(BankAccount, null=True, on_delete=models.CASCADE, default=None)
    bank_transaction_id = models.UUIDField(null=True, default=None, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=now)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(SpendingCategory, null=True, on_delete=models.DO_NOTHING)
    added_at = models.DateTimeField(auto_now_add=True)


class NotificationType(models.TextChoices):
    TRANSACTION = 'TR', 'Transaction'
    ACCOUNT = 'AC', 'Account'
    BUDGET = 'BU', 'Budget'
    GENERAL = 'GE', 'General'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
        max_length=2
    )
    related_object_id = models.UUIDField(null=True, blank=True)


class AppToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_token_id = models.UUIDField(editable=False, unique=True)  # Reference to the bank token ID
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    code = models.CharField(editable=False, max_length=128)
    created_at = models.DateTimeField(editable=False, default=now)
    expires_at = models.DateTimeField(editable=False)
    activated = models.BooleanField(default=False)
