from rest_framework import serializers
from .models import Account, Transaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            'user', 'account_number', 'balance'
        ]

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction  
        fields = [
            'account', 'amount', 'transaction_type','created_at'
        ]      