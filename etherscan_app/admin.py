from django.contrib import admin
from .models import Address, Transaction


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'balance',
                    'created_at', 'last_updated_at', 'last_block_number')
    search_fields = ('address',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_hash', 'address', 'timestamp', 'value')
    list_filter = ('address', 'timestamp')
    search_fields = ('transaction_hash', 'from_address', 'to_address')
