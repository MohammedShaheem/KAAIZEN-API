from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from ...serializers.admin.settlement_serializer import AdminSettlementSerializer
from ...services.admin.admin_wallet_settlement_service import SessionPayoutService


class AdminWalletSettlementView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = AdminSettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data.get("session_id")

        result = SessionPayoutService.settle_session(
            session_id=session_id
        )

        return Response(result, status=status.HTTP_200_OK)