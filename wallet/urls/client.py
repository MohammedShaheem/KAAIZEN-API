from django.urls import path
from wallet.views.client.wallet_view import (
    ClientWalletSummaryView,
    ClientWalletTransactionListView,
)


urlpatterns = [
   
    path("", ClientWalletSummaryView.as_view(), name="client-wallet-summary"),
    path("transactions/", ClientWalletTransactionListView.as_view(), name="client-wallet-transactions"),
]