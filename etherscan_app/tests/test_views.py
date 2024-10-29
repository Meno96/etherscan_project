from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from etherscan_app.models import Address, Transaction
from django.utils import timezone


class FetchTransactionsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('fetch-transactions')
        self.address_data = {
            "address": "0x1234567890abcdef1234567890abcdef12345678"
        }

    @patch('etherscan_app.services.requests.get')
    def test_create_new_address_and_fetch_all_transactions_with_pagination(self, mock_get):
        # Simula una risposta dell'API di Etherscan con 15 transazioni
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "blockNumber": str(12345 + i),
                    "timeStamp": str(1609459200 + i * 100),
                    "hash": f"0xHASH{i}",
                    "from": f"0xFROM{i}",
                    "to": f"0xTO{i}",
                    "value": str(1500000000000000000 + i * 100000000000000000),
                    "gasUsed": str(21000 + i)
                } for i in range(15)
            ]
        }

        # Esegui la richiesta POST per creare un nuovo indirizzo e recuperare tutte le transazioni
        response = self.client.post(self.url, self.address_data, format='json')

        # Verifica che la prima pagina contenga al massimo 10 transazioni (se PAGE_SIZE = 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        # Accedi ai dati sotto `results`
        results = response.data["results"]

        # Verifica la presenza di address e transactions in `results`
        self.assertIn("address", results)
        self.assertIn("transactions", results)

        # Verifica che la prima pagina contenga solo 10 transazioni
        transactions = results["transactions"]
        self.assertEqual(len(transactions), 10)

        # Verifica che il campo `next` non sia None (ci sono più di 10 risultati)
        self.assertIsNotNone(response.data["next"])
        # La prima pagina non ha `previous`
        self.assertIsNone(response.data["previous"])

    @patch('etherscan_app.services.requests.get')
    def test_fetch_only_new_transactions_for_existing_address(self, mock_get):
        # Crea un indirizzo esistente e imposta last_updated_at
        address = Address.objects.create(
            address=self.address_data["address"],
            last_updated_at=timezone.now()
        )

        # Simula la risposta dell'API con una sola nuova transazione
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "blockNumber": "12347",
                    "timeStamp": "1609460000",
                    "hash": "0xHASH789",
                    "from": "0xFROM789",
                    "to": "0xTO789",
                    "value": "2500000000000000000",
                    "gasUsed": "23000"
                }
            ]
        }

        # Esegui la richiesta POST per aggiornare solo le transazioni più recenti
        response = self.client.post(self.url, self.address_data, format='json')

        # Verifica che solo la nuova transazione sia stata salvata
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Accedi ai dati sotto `results`
        results = response.data["results"]

        # Verifica la presenza di address e transactions nella risposta
        self.assertIn("address", results)
        self.assertIn("transactions", results)

        # Verifica i dettagli dell'indirizzo e che il balance sia incluso
        address_data = results["address"]
        self.assertEqual(address_data["address"], self.address_data["address"])
        self.assertIn("balance", address_data)

        # Verifica i dettagli della transazione restituita
        transactions = results["transactions"]
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["transaction_hash"], "0xHASH789")

        # Verifica che last_updated_at sia stato aggiornato
        address.refresh_from_db()
        self.assertIsNotNone(address.last_updated_at)
