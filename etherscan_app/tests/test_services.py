from unittest.mock import patch, Mock
from django.test import TestCase
from django.utils import timezone
from etherscan_app.models import Address, Transaction
from etherscan_app.services import fetch_transactions, fetch_balance


class FetchTransactionsServiceTest(TestCase):
    def setUp(self):
        # Crea un indirizzo di test
        self.address = Address.objects.create(
            address="0x1234567890abcdef1234567890abcdef12345678")

    @patch('etherscan_app.services.requests.get')
    def test_save_all_transactions_for_new_address(self, mock_get):
        # Simula una risposta con due transazioni
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "blockNumber": "12345",
                    "timeStamp": "1609459200",
                    "hash": "0xHASH123",
                    "from": "0xFROM123",
                    "to": "0xTO123",
                    "value": "1500000000000000000",
                    "gasUsed": "21000"
                },
                {
                    "blockNumber": "12346",
                    "timeStamp": "1609459300",
                    "hash": "0xHASH456",
                    "from": "0xFROM456",
                    "to": "0xTO456",
                    "value": "2000000000000000000",
                    "gasUsed": "22000"
                }
            ]
        }

        # Chiama fetch_transactions con un indirizzo nuovo
        fetch_transactions(self.address, updated_only=False)

        # Verifica che le transazioni siano state salvate correttamente
        transactions = Transaction.objects.filter(address=self.address)
        self.assertEqual(transactions.count(), 2)
        self.assertTrue(transactions.filter(
            transaction_hash="0xHASH123").exists())
        self.assertTrue(transactions.filter(
            transaction_hash="0xHASH456").exists())

        # Verifica che last_block_number e last_updated_at siano aggiornati
        self.address.refresh_from_db()
        self.assertEqual(self.address.last_block_number,
                         12346)  # Ultimo blocco salvato
        self.assertIsNotNone(self.address.last_updated_at)

    @patch('etherscan_app.services.requests.get')
    def test_prevent_duplicate_transactions(self, mock_get):
        # Aggiungi una transazione iniziale
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

        # Simula una risposta con una transazione duplicata
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "blockNumber": "12345",
                    "timeStamp": "1609459200",
                    "hash": "0xHASH123",
                    "from": "0xFROM123",
                    "to": "0xTO123",
                    "value": "1500000000000000000",
                    "gasUsed": "21000"
                }
            ]
        }

        # Chiama fetch_transactions e verifica che non venga salvato un duplicato
        fetch_transactions(self.address, updated_only=False)
        transactions = Transaction.objects.filter(address=self.address)
        self.assertEqual(transactions.count(), 1)  # Deve restare 1
        self.assertTrue(transactions.filter(
            transaction_hash="0xHASH123").exists())


class FetchBalanceServiceTest(TestCase):
    def setUp(self):
        # Crea un indirizzo di test
        self.address = Address.objects.create(
            address="0x1234567890abcdef1234567890abcdef12345678")

    @patch('etherscan_app.services.requests.get')
    def test_fetch_balance_success(self, mock_get):
        # Simula una risposta API di Etherscan con un balance in wei
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": "1000000000000000000"  # 1 ETH in wei
        }

        # Chiama fetch_balance e verifica che il balance sia aggiornato
        balance = fetch_balance(self.address)
        self.assertEqual(balance, 1.0)
        self.address.refresh_from_db()
        self.assertEqual(self.address.balance, 1.0)

    @patch('etherscan_app.services.requests.get')
    def test_fetch_balance_network_error(self, mock_get):
        # Simula un errore di rete
        mock_get.side_effect = Exception("Network Error")

        # Chiama fetch_balance e verifica che balance rimanga None
        balance = fetch_balance(self.address)
        self.assertIsNone(balance)
        self.address.refresh_from_db()
        self.assertIsNone(self.address.balance)
