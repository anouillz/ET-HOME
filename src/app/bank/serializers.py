from rest_framework import serializers
from .models import Client, BankAccount, Secret, Token, SpendingCategory, Transaction


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'groups', 'user_permissions'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'user', 'account_number', 'balance', 'bank_name']


class SecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secret
        fields = ['id', 'code', 'account', 'created_at']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = [
            'id', 'code', 'account', 'secret', 'created_at', 'expires_at', 'activated', 'challenge'
        ]


class SpendingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingCategory
        fields = ['id', 'name']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'date', 'description', 'category']

