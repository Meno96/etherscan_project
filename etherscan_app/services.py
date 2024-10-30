import requests
import logging
from datetime import datetime
from django.conf import settings
from .models import Transaction

logger = logging.getLogger(__name__)


def fetch_transactions(address, updated_only=False):
    # Imposta il blocco di partenza se updated_only è True
    start_block = address.last_block_number if updated_only and address.last_block_number else 0

    api_url = (
        f"https://api.etherscan.io/api?module=account&action=txlist"
        f"&address={address.address}&startblock={start_block}&endblock=99999999"
        f"&sort=asc&apikey={settings.ETHERSCAN_API_KEY}"
    )

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json().get("result", [])

        new_transactions = []
        for tx in data:
            transaction_hash = tx["hash"]
            if not Transaction.objects.filter(transaction_hash=transaction_hash).exists():
                # Aggiungi la transazione se non esiste già
                timestamp = datetime.fromtimestamp(int(tx["timeStamp"]))
                block_number = int(tx["blockNumber"])

                Transaction.objects.create(
                    address=address,
                    transaction_hash=transaction_hash,
                    block_number=block_number,
                    timestamp=timestamp,
                    from_address=tx["from"],
                    to_address=tx["to"],
                    value=int(tx["value"]) / 1e18,
                    gas_used=int(tx["gasUsed"]),
                )

                new_transactions.append(tx["hash"])
                logger.info(f"Nuova transazione salvata: {tx['hash']}")

        # Se ci sono nuove transazioni, aggiorna last_block_number e last_updated_at
        if new_transactions:
            address.last_block_number = block_number
            address.last_updated_at = datetime.now()
            address.save()

        # Recupera e aggiorna il balance
        fetch_balance(address)

    except requests.RequestException as e:
        logger.error(f"Errore di rete durante la chiamata API: {e}")
    except Exception as e:
        logger.error(f"Errore imprevisto: {e}")


def fetch_balance(address):
    api_url = (
        f"https://api.etherscan.io/api?module=account&action=balance"
        f"&address={address.address}&tag=latest&apikey={settings.ETHERSCAN_API_KEY}"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json().get("result")
        if data is not None:
            balance = int(data) / 1e18  # Converti wei a ether
            address.balance = balance
            address.save()
            return balance
    except requests.RequestException as e:
        logger.error(f"Errore di rete durante il fetch del balance: {e}")
    except Exception as e:
        logger.error(f"Errore imprevisto nel fetch del balance: {e}")
    return None
