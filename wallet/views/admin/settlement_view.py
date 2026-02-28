from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from wallet.serializers.admin.admin_settlement_serializer import AdminSettlementSerializer
from wallet.services.admin.admin_wallet_settlement_service import AdminWalletSettlementService


class AdminWalletSettlementView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):

        serializer = AdminSettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        settlement_date = serializer.validated_data.get("settlement_date")

        result = AdminWalletSettlementService.settle_for_date(
            settlement_date=settlement_date
        )

        return Response(result, status=status.HTTP_200_OK)