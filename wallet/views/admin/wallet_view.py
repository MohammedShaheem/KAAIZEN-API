import logging
import uuid
from decimal import Decimal

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from wallet.services.admin.wallet_service import (
    AdminWalletOverviewService,
    AdminWalletError,
    DuplicateTransactionError,
    InsufficientBalanceError,
    InvalidAdjustmentError,
    WalletNotFoundError,
)

logger = logging.getLogger(__name__)


class AdminOnlyMixin:
    """Enforces that the caller is an authenticated superuser."""

    permission_classes = [IsAuthenticated]
    

def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() in ("true", "1", "yes")


def _parse_uuid(value: str | None, field_name: str = "id") -> uuid.UUID | None:
    if value is None:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError):
        raise ValidationError({field_name: f"'{value}' is not a valid UUID."})


def _safe_int(value, default: int, min_val: int = 1, max_val: int = 100) -> int:
    try:
        result = int(value)
        return max(min_val, min(result, max_val))
    except (TypeError, ValueError):
        return default


def _service_error_response(exc):
    """Maps service-layer exceptions to appropriate HTTP responses."""
    if isinstance(exc, WalletNotFoundError):
        return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
    if isinstance(exc, InsufficientBalanceError):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    if isinstance(exc, InvalidAdjustmentError):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, DuplicateTransactionError):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    
    return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(never_cache, name="dispatch")
class AdminWalletSummaryView(AdminOnlyMixin, APIView):
  
    def get(self, request):
        try:
            data = AdminWalletOverviewService.get_admin_wallet_summary()
            return Response(data, status=status.HTTP_200_OK)
        except AdminWalletError as exc:
            logger.warning("AdminWalletSummaryView: %s", exc)
            return _service_error_response(exc)
        except Exception as exc:
            logger.exception("AdminWalletSummaryView: unexpected error")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(never_cache, name="dispatch")
class AdminTransactionListView(AdminOnlyMixin, APIView):
    def get(self, request):
        params = request.query_params
        try:
            data = AdminWalletOverviewService.get_admin_transactions(
                entry_type=params.get("entry_type") or None,
                transaction_type=params.get("transaction_type") or None,
                status=params.get("status") or None,
                date_from=params.get("date_from") or None,
                date_to=params.get("date_to") or None,
                search=params.get("search") or None,
                ordering=params.get("ordering", "-created_at"),
                page=_safe_int(params.get("page"), default=1),
                page_size=_safe_int(params.get("page_size"), default=20),
            )
            return Response(data, status=status.HTTP_200_OK)
        except AdminWalletError as exc:
            logger.warning("AdminTransactionListView: %s", exc)
            return _service_error_response(exc)
        except Exception:
            logger.exception("AdminTransactionListView: unexpected error")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(never_cache, name="dispatch")
class AdminMonthlyRevenueView(AdminOnlyMixin, APIView):
    def get(self, request):
        import datetime
        year = _safe_int(
            request.query_params.get("year"),
            default=datetime.datetime.now().year,
            min_val=2000,
            max_val=2100,
        )
        try:
            data = AdminWalletOverviewService.get_monthly_revenue(year=year)
            return Response({"year": year, "monthly_revenue": data}, status=status.HTTP_200_OK)
        except AdminWalletError as exc:
            logger.warning("AdminMonthlyRevenueView: %s", exc)
            return _service_error_response(exc)
        except Exception:
            logger.exception("AdminMonthlyRevenueView: unexpected error")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



@method_decorator(never_cache, name="dispatch")
class PlatformWalletOverviewView(AdminOnlyMixin, APIView):
    def get(self, request):
        try:
            data = AdminWalletOverviewService.get_platform_wallet_overview()
            return Response(data, status=status.HTTP_200_OK)
        except AdminWalletError as exc:
            logger.warning("PlatformWalletOverviewView: %s", exc)
            return _service_error_response(exc)
        except Exception:
            logger.exception("PlatformWalletOverviewView: unexpected error")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(never_cache, name="dispatch")
class AllUserWalletsView(AdminOnlyMixin, APIView):
    def get(self, request):
        params = request.query_params
        try:
            data = AdminWalletOverviewService.get_all_user_wallets(
                role=params.get("role") or None,
                is_active=_parse_bool(params.get("is_active")),
                search=params.get("search") or None,
                ordering=params.get("ordering", "-created_at"),
                page=_safe_int(params.get("page"), default=1),
                page_size=_safe_int(params.get("page_size"), default=20),
            )
            return Response(data, status=status.HTTP_200_OK)
        except AdminWalletError as exc:
            logger.warning("AllUserWalletsView: %s", exc)
            return _service_error_response(exc)
        except Exception:
            logger.exception("AllUserWalletsView: unexpected error")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(never_cache, name="dispatch")
class UserWalletDetailView(AdminOnlyMixin, APIView):

    def get(self, request, wallet_id):
        parsed_id = _parse_uuid(wallet_id, field_name="wallet_id")
        try:
            data = AdminWalletOverviewService.get_user_wallet_detail(wallet_id=parsed_id)
            return Response(data, status=status.HTTP_200_OK)
        except (AdminWalletError, ValidationError) as exc:
            logger.warning("UserWalletDetailView: %s", exc)
            return _service_error_response(exc) if isinstance(exc, AdminWalletError) \
                else Response({"detail": exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception("UserWalletDetailView: unexpected error")
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@method_decorator(never_cache, name="dispatch")
class WalletToggleStatusView(AdminOnlyMixin, APIView):

    def patch(self, request, wallet_id):
        try:
            parsed_id = _parse_uuid(wallet_id, field_name="wallet_id")

            result = AdminWalletOverviewService.toggle_wallet_status(
                wallet_id=parsed_id,
                performed_by_user=request.user,
            )

            return Response(result, status=status.HTTP_200_OK)

        except ValidationError as exc:
            logger.warning(
                "WalletToggleStatusView validation error [wallet=%s]: %s",
                wallet_id, exc
            )
            return Response(
                {"detail": exc.detail},
                status=status.HTTP_400_BAD_REQUEST
            )

        except AdminWalletError as exc:
            logger.warning(
                "WalletToggleStatusView service error [wallet=%s]: %s",
                wallet_id, exc
            )
            return _service_error_response(exc)

        except Exception:
            logger.exception(
                "WalletToggleStatusView unexpected error [wallet=%s]",
                wallet_id
            )
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )