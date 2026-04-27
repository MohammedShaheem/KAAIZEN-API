import logging
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model

from personal_training.models import TrainingSession
from wallet.models import Wallet, WalletTransaction

User = get_user_model()
logger = logging.getLogger(__name__)


class RefundServiceError(Exception):
    pass


class SessionRefundService:

    @staticmethod
    def _get_admin_user():
        admin = User.objects.filter(is_superuser=True, is_active=True).first()
        if not admin:
            raise RefundServiceError("No active admin user found for refund processing.")
        return admin

    @staticmethod
    def _resolve_refund_amount(session):
        if session.session_price:
            return Decimal(str(session.session_price))

        if session.client_plan and session.client_plan.per_session_price:
            return Decimal(str(session.client_plan.per_session_price))

        raise RefundServiceError(
            f"Cannot determine refund amount for session {session.id}. "
            "Neither session_price nor per_session_price is set."
        )

    @staticmethod
    @transaction.atomic
    def process_session_refund(session, reason):

        session = (
            TrainingSession.objects
            .select_for_update(of=("self",))
            .get(id=session.id)
        )

        if session.wallet_processed:
            logger.info(
                "SessionRefundService: session %s already wallet_processed. Skipping.",
                session.id,
            )
            return {"skipped": True, "session_id": str(session.id)}

        refund_amount = SessionRefundService._resolve_refund_amount(session)
        client_user   = session.client.user
        admin_user    = SessionRefundService._get_admin_user()

        try:
            admin_wallet = Wallet.objects.select_for_update().get(
                user=admin_user, is_active=True
            )
        except Wallet.DoesNotExist:
            raise RefundServiceError("Admin wallet not found or inactive.")

        if admin_wallet.balance < refund_amount:
            raise RefundServiceError(
                f"Admin wallet has insufficient balance for refund. "
                f"Available: {admin_wallet.balance}, Required: {refund_amount}"
            )
            
        descriptions = {
            "system_no_trainer": (
                f"Refund — session on {session.session_date} cancelled "
                "(no trainer available)."
            ),
            "client_early_cancel": (
                f"Refund — session on {session.session_date} cancelled "
                "by client within policy."
            ),
            "trainer_no_show": (         
                f"Refund — session on {session.session_date} cancelled "
                "(trainer did not join)."
            ),
        }
        description = descriptions.get(reason, f"Refund — session on {session.session_date}.")
        desc_debit  = f"Refund debit — {description}"
        desc_credit = f"Refund credit — {description}"

        idempotency_suffix = f"{reason}_{session.id}"

        
        admin_balance_before  = admin_wallet.balance
        admin_wallet.balance -= refund_amount
        admin_wallet.save(update_fields=["balance", "updated_at"])

        WalletTransaction.objects.create(
            wallet=admin_wallet,
            from_user=admin_user,
            to_user=client_user,
            amount=refund_amount,
            entry_type="debit",
            transaction_type="session_refund",
            reference_id=session.id,
            status="success",
            balance_before=admin_balance_before,
            balance_after=admin_wallet.balance,
            idempotency_key=f"admin_refund_debit_{idempotency_suffix}",
            description=desc_debit,
        )

        
        try:
            client_wallet = Wallet.objects.select_for_update().get(
                user=client_user, is_active=True
            )
        except Wallet.DoesNotExist:
            raise RefundServiceError(
                f"Client wallet not found or inactive for user {client_user.id}."
            )

        client_balance_before  = client_wallet.balance
        client_wallet.balance += refund_amount
        client_wallet.save(update_fields=["balance", "updated_at"])

        WalletTransaction.objects.create(
            wallet=client_wallet,
            from_user=admin_user,
            to_user=client_user,
            amount=refund_amount,
            entry_type="credit",
            transaction_type="session_refund",
            reference_id=session.id,
            status="success",
            balance_before=client_balance_before,
            balance_after=client_wallet.balance,
            idempotency_key=f"client_refund_credit_{idempotency_suffix}",
            description=desc_credit,
        )

        
        session.wallet_processed = True
        session.save(update_fields=["wallet_processed"])

        logger.info(
            "SessionRefundService: refund completed for session %s | "
            "amount=%s | client=%s",
            session.id, refund_amount, client_user.id,
        )

        return {
            "session_id":     str(session.id),
            "refund_amount":  str(refund_amount),
            "client_user_id": str(client_user.id),
        }