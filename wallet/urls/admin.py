from django.urls import path

from wallet.views.admin.wallet_view import (
    AdminMonthlyRevenueView,
    AdminTransactionListView,
    AdminWalletSummaryView,
    AllUserWalletsView,
    PlatformWalletOverviewView,
    UserWalletDetailView,
    WalletToggleStatusView,
)

app_name = "admin_wallet"

urlpatterns = [
    path(
        "summary/",
        AdminWalletSummaryView.as_view(),
        name="admin-wallet-summary",
    ),
    path(
        "transactions/",
        AdminTransactionListView.as_view(),
        name="admin-wallet-transactions",
    ),
    path(
        "revenue/monthly/",
        AdminMonthlyRevenueView.as_view(),
        name="admin-wallet-monthly-revenue",
    ),

    path(
        "platform/overview/",
        PlatformWalletOverviewView.as_view(),
        name="platform-wallet-overview",
    ),

    path(
        "users/",
        AllUserWalletsView.as_view(),
        name="all-user-wallets",
    ),
    path(
        "users/<uuid:wallet_id>/",
        UserWalletDetailView.as_view(),
        name="user-wallet-detail",
    ),

    path(
        "users/<uuid:wallet_id>/toggle-status/",
        WalletToggleStatusView.as_view(),
        name="wallet-toggle-status",
    ),
]