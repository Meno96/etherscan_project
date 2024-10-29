from django.db import models


class Address(models.Model):
    address = models.CharField(max_length=42, unique=True)
    balance = models.DecimalField(max_digits=20, decimal_places=8, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_block_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.address


class Transaction(models.Model):
    address = models.ForeignKey(
        Address, related_name="transactions", on_delete=models.CASCADE)
    transaction_hash = models.CharField(max_length=66, primary_key=True)
    block_number = models.IntegerField()
    timestamp = models.DateTimeField()
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    value = models.DecimalField(max_digits=20, decimal_places=8)
    gas_used = models.IntegerField()

    def __str__(self):
        return self.transaction_hash
