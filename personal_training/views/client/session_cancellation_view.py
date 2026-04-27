from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from clients.permissions import IsClient
from personal_training.serializers.client.session_cancellation import (
    SessionCancellationSerializer
)
from clients.models import ClientProfile
from personal_training.services.client.session_cancellation_service import (
    SessionCancellationService
)
import logging

logger = logging.getLogger(__name__)
class SessionCancellationView(APIView):
    
    permission_classes = [IsClient]

    def post(self, request):
        serializer = SessionCancellationSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            try:
                client = request.user.client_profile
            except ClientProfile.DoesNotExist:
                return Response(
                    {"detail": "Client profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            session_id = serializer.validated_data["session_id"]

            result = SessionCancellationService.cancel_session(
                client=client,
                session_id=session_id
            )

            return Response(
                {
                    "message": "Session canceled successfully.",
                    "refund_eligible": result["refund_eligible"],
                    "cancellations_used": result["cancellations_used"],
                    "remaining_cancellations": result[
                        "remaining_cancellations"
                    ],
                    "session_status": result["session"].status
                },
                status=status.HTTP_200_OK
            )

        except ValidationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.exception("Session cancellation failed")  
        return Response(
            {"detail": "Something went wrong while canceling session."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
