from django.urls import path
from .views import transaction_list_view, FetchTransactionsView

urlpatterns = [
    path('transactions/', transaction_list_view, name='transaction-list-view'),
    path('api/addresses/fetch_transactions/',
         FetchTransactionsView.as_view(), name='fetch-transactions'),
]
