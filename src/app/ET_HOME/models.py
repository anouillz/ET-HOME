from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils.timezone import now
import pyotp # otp plugin for double auth (prototype now just an example)

'''
import qrcode
import qrcode.image.svg
import qrcode
import qrcode.image.svg
from io import BytesIO
for generating qrcode of otp
'''

class User(AbstractUser):
    otp_secret = models.CharField(max_length=16, blank=True, null=True)     # double auth with otp

    def generate_otp_secret(self):
        self.otp_secret = pyotp.random_base32()
        self.save()

    def get_otp_uri(self):
        return pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.email,
            issuer_name="ET-HOME"
        )

    def verify_otp(self, otp):
        totp = pyotp.TOTP(self.otp_secret)
        return totp.verify(otp)

class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    secret = models.CharField(max_length=128)


class SpendingCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=now)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(SpendingCategory,on_delete=models.DO_NOTHING)
    
class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(SpendingCategory,on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=20)

class NotificationType(models.TextChoices):
    TRANSACTION = 'TR', 'Transaction'
    ACCOUNT = 'AC', 'Account'
    BUDGET = 'BU', 'Budget'
    INSIGHT = 'IN', 'Insight'
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
'''
done in graphical interface with graphs plugin ?
class FinancialInsight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    insight_type = models.CharField(max_length=50)
    description = models.TextField()
    date_generated = models.DateTimeField(auto_now_add=True)
'''
