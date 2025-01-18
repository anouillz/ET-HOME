import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class Client(AbstractUser):
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="bank_user_set",
        blank=True,
        help_text="The gruops this user blongs to",
        verbose_name="groups"
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="bank_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user",
        verbose_name="user permissions"
    )

class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=100)

class Secret(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(editable=False,max_length=128)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    created_at = models.DateTimeField(editable=False,default=now)

class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(editable=False,max_length=128)
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    secret = models.ForeignKey(Secret, on_delete=models.CASCADE)
    created_at = models.DateTimeField(editable=False,default=now)
    expires_at = models.DateTimeField(editable=False)
    activated = models.BooleanField(default=False),
    challenge = models.CharField(editable=False,max_length=32)
    
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




