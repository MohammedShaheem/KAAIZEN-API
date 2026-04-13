import logging
from django.db.models import QuerySet

from wallet.models import Wallet, WalletTransaction
from users.models import User
from users.choices import UserRole

logger = logging.getLogger(__name__)


class TrainerWalletServiceException(Exception):
    pass


class TrainerWalletService:

    @staticmethod
    def _get_trainer_wallet(user: User) -> Wallet:
        """
        Fetch wallet for a verified trainer user.
        Raises TrainerWalletServiceException on any failure.
        """
        if user.role != UserRole.TRAINER:
            logger.warning(
                "Non-trainer user %s attempted to access trainer wallet.", user.id
            )
            raise TrainerWalletServiceException("User is not a trainer.")

        try:
            wallet = Wallet.objects.select_related("user").get(user=user, is_active=True)
        except Wallet.DoesNotExist:
            logger.error("Active wallet not found for trainer user %s.", user.id)
            raise TrainerWalletServiceException("Wallet not found or inactive.")

        return wallet

    @staticmethod
    def get_wallet_summary(user: User) -> dict:
        """
        Returns wallet balance and currency for a trainer.
        """
        wallet = TrainerWalletService._get_trainer_wallet(user)

        return {
            "wallet_id": str(wallet.id),
            "balance": wallet.balance,
            "currency": wallet.currency,
            "is_active": wallet.is_active,
        }

    @staticmethod
    def get_wallet_transactions(user: User) -> QuerySet:
        """
        Returns the base queryset of transactions for a trainer's wallet.
        Filtering, ordering, and pagination are handled at the view layer.
        """
        wallet = TrainerWalletService._get_trainer_wallet(user)

        return (
            WalletTransaction.objects
            .filter(wallet=wallet)
            .select_related("from_user", "to_user")
            .order_by("-created_at")
        )