from celery import shared_task
from wallet.services.admin.admin_wallet_settlement_service import AdminWalletSettlementService


@shared_task
def run_admin_daily_settlement():
    return AdminWalletSettlementService.settle_for_date()