import logging
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet

from wallet.models import Wallet, WalletTransaction
from users.models import User
from users.choices import UserRole

logger = logging.getLogger(__name__)


class ClientWalletServiceException(Exception):
    pass


class ClientWalletService:

    @staticmethod
    def _get_client_wallet(user: User) -> Wallet:
        """
        Fetch wallet for a verified client user.
        Raises ClientWalletServiceException on any failure.
        """
        if user.role != UserRole.CLIENT:
            logger.warning(
                "Non-client user %s attempted to access client wallet.", user.id
            )
            raise ClientWalletServiceException("User is not a client.")

        try:
            wallet = Wallet.objects.select_related("user").get(user=user, is_active=True)
        except Wallet.DoesNotExist:
            logger.error("Active wallet not found for client user %s.", user.id)
            raise ClientWalletServiceException("Wallet not found or inactive.")

        return wallet

    @staticmethod
    def get_wallet_summary(user):
        """
        Returns wallet balance and currency for a client.
        """
        wallet = ClientWalletService._get_client_wallet(user)

        return {
            "wallet_id": str(wallet.id),
            "balance": wallet.balance,
            "currency": wallet.currency,
            "is_active": wallet.is_active,
        }

    @staticmethod
    def get_wallet_transactions(user):
        """
        Returns the base queryset of transactions for a client's wallet.
        Filtering, ordering, and pagination are handled at the view layer.
        """
        wallet = ClientWalletService._get_client_wallet(user)

        return (
            WalletTransaction.objects
            .filter(wallet=wallet)
            .select_related("from_user", "to_user")
            .order_by("-created_at")
        )