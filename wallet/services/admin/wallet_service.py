import logging
from decimal import Decimal, InvalidOperation
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import (
    DecimalField,
    F,
    Q,
    Sum,
    Count,
    Value,
    ExpressionWrapper,
)
from django.db.models.functions import Coalesce, TruncDate, TruncMonth
from django.utils import timezone

from wallet.models import Wallet, WalletTransaction

User = get_user_model()
logger = logging.getLogger(__name__)




class AdminWalletError(Exception):
    """Base exception for admin wallet operations."""


class InsufficientBalanceError(AdminWalletError):
    """Raised when a debit would push the wallet below zero."""


class WalletNotFoundError(AdminWalletError):
    """Raised when the target wallet cannot be located."""


class InvalidAdjustmentError(AdminWalletError):
    """Raised when adjustment parameters are invalid."""


class DuplicateTransactionError(AdminWalletError):
    """Raised when an idempotency key is already present."""



def _get_admin_user():
    admin = User.objects.filter(is_superuser=True, is_active=True).first()
    if not admin:
        raise AdminWalletError("No active superuser found.")
    return admin


def _get_admin_wallet(admin_user=None):
    if admin_user is None:
        admin_user = _get_admin_user()
    try:
        return Wallet.objects.select_for_update().get(user=admin_user, is_active=True)
    except Wallet.DoesNotExist:
        raise WalletNotFoundError("Admin wallet does not exist or is inactive.")



class AdminWalletOverviewService:

    @staticmethod
    def get_admin_wallet_summary():
       
        admin_user = _get_admin_user()
        
        try:
            wallet = Wallet.objects.get(user=admin_user)
            
        except Wallet.DoesNotExist:
            raise WalletNotFoundError("Admin wallet not found.")

        qs = WalletTransaction.objects.filter(wallet=wallet)

        totals = qs.aggregate(
            total_credited=Coalesce(
                Sum("amount", filter=Q(entry_type="credit", status="success")),
                Decimal("0.00"),
                output_field=DecimalField(),
            ),
            total_debited=Coalesce(
                Sum("amount", filter=Q(entry_type="debit", status="success")),
                Decimal("0.00"),
                output_field=DecimalField(),
            ),
            total_transactions=Count("id"),
        )

        return {
            "wallet_id": str(wallet.id),
            "balance": wallet.balance,
            "currency": wallet.currency,
            "is_active": wallet.is_active,
            "total_credited": totals["total_credited"],
            "total_debited": totals["total_debited"],
            "total_transactions": totals["total_transactions"],
            "last_updated": wallet.updated_at,
        }

    @staticmethod
    def get_admin_transactions(
        *,
        entry_type: Optional[str] = None,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
        date_from=None,
        date_to=None,
        search: Optional[str] = None,
        ordering: str = "-created_at",
        page: int = 1,
        page_size: int = 20,):
        
        admin_user = _get_admin_user()
        
        try:
            wallet = Wallet.objects.get(user=admin_user)
        
        except Wallet.DoesNotExist:
            raise WalletNotFoundError("Admin wallet not found.")

        qs = WalletTransaction.objects.filter(wallet=wallet).select_related(
            "from_user", "to_user"
        )

        if entry_type:
            qs = qs.filter(entry_type=entry_type)
        if transaction_type:
            qs = qs.filter(transaction_type=transaction_type)
        if status:
            qs = qs.filter(status=status)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        if search:
            qs = qs.filter(
                Q(description__icontains=search)
                | Q(reference_id__icontains=search)
                | Q(idempotency_key__icontains=search)
            )

        allowed_orderings = {
            "created_at", "-created_at",
            "amount", "-amount",
            "status", "-status",
        }
        if ordering not in allowed_orderings:
            ordering = "-created_at"

        qs = qs.order_by(ordering)

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        return {
            "results": list(page_obj.object_list.values(
                "id", "entry_type", "transaction_type", "amount",
                "status", "balance_before", "balance_after",
                "reference_id", "description", "created_at",
                "from_user__id", "from_user__email",
                "to_user__id", "to_user__email",
            )),
            "pagination": {
                "page": page_obj.number,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }

    @staticmethod
    def get_platform_wallet_overview():
        
        wallets_qs = Wallet.objects.select_related("user")

        role_summary = {}
        for role in ("client", "trainer", "admin"):
            agg = wallets_qs.filter(user__role=role).aggregate(
                count=Count("id"),
                total_balance=Coalesce(
                    Sum("balance"), Decimal("0.00"), output_field=DecimalField()
                ),
            )
            role_summary[role] = agg

        tx_agg = WalletTransaction.objects.aggregate(
            platform_total_credited=Coalesce(
                Sum("amount", filter=Q(entry_type="credit", status="success")),
                Decimal("0.00"),
                output_field=DecimalField(),
            ),
            platform_total_debited=Coalesce(
                Sum("amount", filter=Q(entry_type="debit", status="success")),
                Decimal("0.00"),
                output_field=DecimalField(),
            ),
            total_transactions=Count("id"),
            pending_count=Count("id", filter=Q(status="pending")),
            failed_count=Count("id", filter=Q(status="failed")),
        )

        return {
            "role_wallets": role_summary,
            "transaction_summary": tx_agg,
        }

    @staticmethod
    def get_monthly_revenue(year: int) -> list:
        
        admin_user = _get_admin_user()
        try:
            wallet = Wallet.objects.get(user=admin_user)
        except Wallet.DoesNotExist:
            raise WalletNotFoundError("Admin wallet not found.")

        data = (
            WalletTransaction.objects.filter(
                wallet=wallet,
                entry_type="credit",
                status="success",
                created_at__year=year,
            )
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                total=Sum("amount"),
                count=Count("id"),
            )
            .order_by("month")
        )
        return list(data)

    

    @staticmethod
    def get_all_user_wallets(
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        ordering: str = "-created_at",
        page: int = 1,
        page_size: int = 20,
    ):

        qs = Wallet.objects.select_related("user").all()

        if role:
            qs = qs.filter(user__role=role)

        if is_active is not None:
            qs = qs.filter(is_active=is_active)

        
        if search:
            qs = qs.filter(
                Q(user__email__icontains=search)
                | Q(user__username__icontains=search)
            )

        allowed_orderings = {
            "balance", "-balance",
            "created_at", "-created_at",
            "user__email", "-user__email",
        }

        if ordering not in allowed_orderings:
            ordering = "-created_at"

        qs = qs.order_by(ordering)

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        return {
            "results": list(page_obj.object_list.values(
                "id",
                "balance",
                "currency",
                "is_active",
                "created_at",
                "updated_at",
                "user__id",
                "user__email",
                "user__username",   
                "user__role",
            )),
            "pagination": {
                "page": page_obj.number,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }

    @staticmethod
    def get_user_wallet_detail(wallet_id):

        try:
            wallet = Wallet.objects.select_related("user").get(id=wallet_id)
        except Wallet.DoesNotExist:
            raise WalletNotFoundError(f"Wallet {wallet_id} not found.")

        tx_agg = WalletTransaction.objects.filter(wallet=wallet).aggregate(
            total_credited=Coalesce(
                Sum("amount", filter=Q(entry_type="credit", status="success")),
                Decimal("0.00"),
                output_field=DecimalField(),
            ),
            total_debited=Coalesce(
                Sum("amount", filter=Q(entry_type="debit", status="success")),
                Decimal("0.00"),
                output_field=DecimalField(),
            ),
            total_transactions=Count("id"),
        )

        return {
            "wallet_id": str(wallet.id),
            "balance": wallet.balance,
            "currency": wallet.currency,
            "is_active": wallet.is_active,
            "created_at": wallet.created_at,
            "updated_at": wallet.updated_at,
            "user": {
                "id": str(wallet.user.id),
                "email": wallet.user.email,
                "full_name": getattr(wallet.user, "username", "") or wallet.user.email,
                "role": getattr(wallet.user, "role", None),
            },
            **tx_agg,
        }

    @staticmethod
    @transaction.atomic
    def toggle_wallet_status(
        *,
        wallet_id: UUID,
        performed_by_user,):
        
        try:
            wallet = Wallet.objects.select_for_update(nowait=True).select_related(
                "user"
            ).get(id=wallet_id)
        except Wallet.DoesNotExist:
            raise WalletNotFoundError(f"Wallet {wallet_id} not found.")

        if wallet.user == performed_by_user:
            raise InvalidAdjustmentError("Admin cannot deactivate their own wallet.")

        wallet.is_active = not wallet.is_active
        wallet.save(update_fields=["is_active", "updated_at"])

        logger.info(
            "AdminWalletAdjustmentService: wallet %s set is_active=%s by admin %s",
            wallet_id, wallet.is_active, performed_by_user.email,
        )

        return {
            "wallet_id": str(wallet.id),
            "is_active": wallet.is_active,
        }