from django.test import TestCase
from etherscan_app.models import Address, Transaction
from datetime import datetime
from django.utils import timezone


class AddressModelTest(TestCase):
    def test_can_create_address(self):
        # Creazione di un indirizzo
        address = Address.objects.create(
            address="0x1234567890abcdef1234567890abcdef12345678"
        )

        # Verifica che l'indirizzo sia stato creato correttamente
        self.assertEqual(
            address.address, "0x1234567890abcdef1234567890abcdef12345678")
        # Verifica che last_block_number sia inizialmente None
        self.assertIsNone(address.last_block_number)
        self.assertIsNotNone(address.created_at)
        self.assertIsNotNone(address.last_updated_at)

    def test_address_uniqueness(self):
        # Test sull'unicità dell'indirizzo
        Address.objects.create(
            address="0x1234567890abcdef1234567890abcdef12345678"
        )

        with self.assertRaises(Exception):
            Address.objects.create(
                address="0x1234567890abcdef1234567890abcdef12345678"
            )

    def test_update_last_block_number(self):
        # Creazione di un indirizzo e aggiornamento di last_block_number
        address = Address.objects.create(
            address="0x1234567890abcdef1234567890abcdef12345678"
        )
        address.last_block_number = 12345
        address.save()

        # Verifica che last_block_number sia aggiornato correttamente
        address.refresh_from_db()
        self.assertEqual(address.last_block_number, 12345)


class TransactionModelTest(TestCase):
    def setUp(self):
        # Crea un indirizzo di test per collegare le transazioni
        self.address = Address.objects.create(
            address="0x1234567890abcdef1234567890abcdef12345678"
        )

    def test_can_create_transaction(self):
        # Creazione di una transazione collegata a un indirizzo
        transaction = Transaction.objects.create(
            address=self.address,
            transaction_hash="0xHASH123",
            block_number=12345,
            timestamp=timezone.now(),
            from_address="0xFROM123",
            to_address="0xTO123",
            value=1.5,
            gas_used=21000
        )

        # Verifica che la transazione sia stata creata correttamente
        self.assertEqual(transaction.transaction_hash, "0xHASH123")
        self.assertEqual(transaction.block_number, 12345)
        self.assertEqual(transaction.from_address, "0xFROM123")
        self.assertEqual(transaction.to_address, "0xTO123")
        self.assertEqual(transaction.value, 1.5)
        self.assertEqual(transaction.gas_used, 21000)
        self.assertIsNotNone(transaction.timestamp)

    def test_transaction_uniqueness(self):
        # Creazione di una transazione unica
        Transaction.objects.create(
            address=self.address,
            transaction_hash="0xHASH123",
            block_number=12345,
            timestamp=timezone.now(),
            from_address="0xFROM123",
            to_address="0xTO123",
            value=1.5,
            gas_used=21000
        )

        # Verifica che una transazione con lo stesso hash sollevi un'eccezione
        with self.assertRaises(Exception):
            Transaction.objects.create(
                address=self.address,
                transaction_hash="0xHASH123",
                block_number=12346,
                timestamp=timezone.now(),
                from_address="0xFROM456",
                to_address="0xTO456",
                value=2.0,
                gas_used=22000
            )

    def test_address_transaction_relationship(self):
        # Creazione di transazioni collegate all'indirizzo
        transaction1 = Transaction.objects.create(
            address=self.address,
            transaction_hash="0xHASH123",
            block_number=12345,
            timestamp=timezone.now(),
            from_address="0xFROM123",
            to_address="0xTO123",
            value=1.5,
            gas_used=21000
        )

        transaction2 = Transaction.objects.create(
            address=self.address,
            transaction_hash="0xHASH456",
            block_number=12346,
            timestamp=timezone.now(),
            from_address="0xFROM456",
            to_address="0xTO456",
            value=2.0,
            gas_used=22000
        )

        # Verifica la relazione uno-a-molti tra Address e Transaction
        transactions = self.address.transactions.all()
        self.assertEqual(transactions.count(), 2)
        self.assertIn(transaction1, transactions)
        self.assertIn(transaction2, transactions)
