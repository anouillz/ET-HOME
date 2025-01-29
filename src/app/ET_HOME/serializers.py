from rest_framework import serializers

from .models import Notification, Transaction, BankAccount, SpendingCategory, User


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'message',
            'date',
            'is_read',
            'type',
            'related_object_id',
        ]


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = (
            "id",
            "account_number"
        )

class FullBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = (
            "id",
            "account_number",
            "balance",
            "bank_name"
        )

class SpendingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingCategory
        fields = (
            "id",
            "name"
        )

class FullSpendingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingCategory
        fields = (
            "id",
            "name",
            "is_default",
            "user_budget"
        )

class TransactionSerializer(serializers.ModelSerializer):
    account = BankAccountSerializer()
    category = SpendingCategorySerializer()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "amount",
            "date",
            "description",
            "category"
        )

class TransactionWithoutCategorySerializer(serializers.ModelSerializer):
    account = BankAccountSerializer()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "amount",
            "date",
            "description"
        )


class TransactionWithoutAccountSerializer(serializers.ModelSerializer):
    category = SpendingCategorySerializer()

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category",
            "amount",
            "date",
            "description"
        )

class BareTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "account",
            "category",
            "amount",
            "date",
            "description"
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "last_login",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined"
        )