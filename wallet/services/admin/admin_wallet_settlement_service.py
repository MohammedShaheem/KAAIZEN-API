from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from personal_training.models import TrainingSession
from wallet.models import Wallet, WalletTransaction
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminWalletSettlementService:

    @staticmethod
    @transaction.atomic
    def settle_for_date(settlement_date=None):

        if not settlement_date:
            settlement_date = timezone.now().date() - timedelta(days=1)

        sessions = TrainingSession.objects.select_for_update().filter(
            session_date=settlement_date,
            status="completed",
            wallet_processed=False
        )

        total_admin_amount = sessions.aggregate(
            total=Sum("admin_share_amount")
        )["total"] or Decimal("0.00")

        if total_admin_amount == Decimal("0.00"):
            return {
                "message": "No sessions to settle",
                "total_amount": Decimal("0.00"),
                "sessions_count": 0
            }

        admin_user = User.objects.get(is_superuser=True)
        admin_wallet = Wallet.objects.select_for_update().get(user=admin_user)

        
        admin_wallet.balance += total_admin_amount
        admin_wallet.save(update_fields=["balance"])

        
        WalletTransaction.objects.create(
            wallet=admin_wallet,
            amount=total_admin_amount,
            entry_type="credit",
            transaction_type="daily_admin_settlement",
            reference_id=None
        )

        
        sessions.update(wallet_processed=True)

        return {
            "message": "Settlement successful",
            "total_amount": total_admin_amount,
            "sessions_count": sessions.count()
        }