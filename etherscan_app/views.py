from datetime import datetime
import logging

from django.utils import timezone
from django.conf import settings
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Address, Transaction
from .serializers import AddressSerializer, TransactionSerializer
from .services import fetch_transactions


class FetchTransactionsView(APIView):
    def post(self, request):
        address_str = request.data.get("address")

        if not address_str:
            return Response({"error": "Address is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Ottieni o crea l'indirizzo nel database
        address, created = Address.objects.get_or_create(address=address_str)

        # Esegui fetch_transactions per aggiornare le transazioni e il balance
        fetch_transactions(address, updated_only=not created)

        # Recupera tutte le transazioni aggiornate per l'indirizzo
        transactions = Transaction.objects.filter(
            address=address).order_by('-timestamp')

        # Pagina i risultati
        paginator = PageNumberPagination()
        paginated_transactions = paginator.paginate_queryset(
            transactions, request)
        transactions_data = TransactionSerializer(
            paginated_transactions, many=True).data

        return paginator.get_paginated_response(
            {
                "address": AddressSerializer(address).data,
                "transactions": transactions_data
            }
        )


def transaction_list_view(request):
    return render(request, 'etherscan_app/transaction_list.html')
