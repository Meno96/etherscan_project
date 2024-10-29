from rest_framework import serializers
from .models import Address, Transaction


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address', 'balance', 'created_at', 'last_updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'transaction_hash', 'block_number', 'timestamp', 'from_address',
            'to_address', 'value', 'gas_used', 'address'
        ]
