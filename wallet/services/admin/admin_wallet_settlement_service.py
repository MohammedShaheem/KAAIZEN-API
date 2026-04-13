import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

from personal_training.models import TrainingSession
from wallet.models import Wallet, WalletTransaction

User = get_user_model()
logger = logging.getLogger(__name__)

ADMIN_SHARE_PERCENT = Decimal("0.10")
TRAINER_SHARE_PERCENT = Decimal("0.90")


class SessionPayoutService:
    """
    Settles a single completed session atomically.
    - Credits trainer wallet with 90%
    - Credits admin wallet with 10%
    - Both WalletTransactions carry reference_id = session.id
    - Idempotent: raises if session already processed
    """

    @staticmethod
    @transaction.atomic
    def settle_session(session_id):
        try:
            session = TrainingSession.objects.select_for_update(nowait=True).get(
                id=session_id,
                status="completed",
                wallet_processed=False,
            )
            print("session",session)
        except TrainingSession.DoesNotExist:
            logger.warning(
                f"SessionPayoutService: session {session_id} not found, "
                "already processed, or not completed. Skipping."
            )
            return {"skipped": True, "session_id": str(session_id)}

        session_fee = session.session_price or Decimal("0.00")
        trainer_amount = session.trainer_share_amount
        admin_amount = session.admin_share_amount

        
        trainer_wallet = Wallet.objects.select_for_update().get(
            user=session.trainer.user
        )
        trainer_balance_before = trainer_wallet.balance
        trainer_wallet.balance += trainer_amount
        trainer_wallet.save()
        
        
        admin_user = SessionPayoutService._get_admin_user()

        WalletTransaction.objects.create(
            wallet=trainer_wallet,
            from_user=admin_user,
            to_user=session.trainer.user,
            amount=trainer_amount,
            entry_type="credit",
            transaction_type="session_earning",
            reference_id=session.id,
            status="success",
            balance_before=trainer_balance_before,
            balance_after=trainer_wallet.balance,
            idempotency_key=f"trainer_payout_{session.id}",
            description=(
                f"Earning from session on {session.session_date} "
            ),
        )

        
        admin_user = SessionPayoutService._get_admin_user()
        admin_wallet = Wallet.objects.select_for_update().get(user=admin_user)
        admin_balance_before = admin_wallet.balance
        admin_wallet.balance += admin_amount
        admin_wallet.save(update_fields=["balance", "updated_at"])

        WalletTransaction.objects.create(
            wallet=admin_wallet,
            amount=admin_amount,
            entry_type="credit",
            transaction_type="session_platform_fee",
            reference_id=session.id,
            status="success",
            balance_before=admin_balance_before,
            balance_after=admin_wallet.balance,
            idempotency_key=f"admin_payout_{session.id}",
            description=(
                f"Platform fee — session {session.session_date} "
                
            ),
        )

        
        session.wallet_processed = True
        session.save()

        logger.info(
            f"SessionPayoutService: settled session {session_id} | "
            f"trainer={trainer_amount} admin={admin_amount}"
        ) 

        return {
            "session_id": str(session_id),
            "trainer_amount": trainer_amount,
            "admin_amount": admin_amount,
        }

    @staticmethod
    def _get_admin_user():
        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            raise ValueError("No admin user found for platform fee settlement.")
        return admin