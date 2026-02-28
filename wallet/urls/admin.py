from django.urls import path
from wallet.views.admin.settlement_view import AdminWalletSettlementView
urlpatterns = [
    path("settlement",AdminWalletSettlementView.as_view())
]
