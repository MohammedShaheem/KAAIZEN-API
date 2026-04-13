import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from wallet.services.trainer.wallet_service   import (
    TrainerWalletService,
    TrainerWalletServiceException,
)
from wallet.serializers.common.wallet_serializer import WalletSummarySerializer, WalletTransactionSerializer
from wallet.filters import TrainerTransactionFilter
from users.choices import UserRole

logger = logging.getLogger(__name__)


class IsTrainer(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.role == UserRole.TRAINER
        )


class WalletTransactionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TrainerWalletSummaryView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        try:
            summary = TrainerWalletService.get_wallet_summary(request.user)
            serializer = WalletSummarySerializer(summary)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TrainerWalletServiceException as exc:
            logger.warning(
                "TrainerWalletSummaryView error for user %s: %s", request.user.id, exc
            )
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception(
                "Unexpected error in TrainerWalletSummaryView for user %s", request.user.id
            )
            return Response(
                {"detail": "An unexpected error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TrainerWalletTransactionListView(APIView):
    permission_classes = [IsTrainer]

    def get(self, request):
        try:
            queryset = TrainerWalletService.get_wallet_transactions(request.user)

            # Apply filters
            filterset = TrainerTransactionFilter(request.GET, queryset=queryset)
            if not filterset.is_valid():
                return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
            queryset = filterset.qs

            # Apply ordering
            ordering = request.query_params.get("ordering", "-created_at")
            allowed_ordering = {
                "created_at", "-created_at",
                "amount", "-amount",
                "status", "-status",
                "entry_type", "-entry_type",
            }
            if ordering in allowed_ordering:
                queryset = queryset.order_by(ordering)

            # Paginate
            paginator = WalletTransactionPagination()
            page = paginator.paginate_queryset(queryset, request, view=self)
            serializer = WalletTransactionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except TrainerWalletServiceException as exc:
            logger.warning(
                "TrainerWalletTransactionListView error for user %s: %s", request.user.id, exc
            )
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.exception(
                "Unexpected error in TrainerWalletTransactionListView for user %s", request.user.id
            )
            return Response(
                {"detail": "An unexpected error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )