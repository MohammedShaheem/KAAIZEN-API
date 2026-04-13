from django.urls import path

from wallet.views.trainer.wallet_view import (
    TrainerWalletSummaryView,
    TrainerWalletTransactionListView,
)

urlpatterns = [
    path("", TrainerWalletSummaryView.as_view(), name="trainer-wallet-summary"),
    path("transactions/", TrainerWalletTransactionListView.as_view(), name="trainer-wallet-transactions"),
]