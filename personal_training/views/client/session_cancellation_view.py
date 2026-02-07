from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from clients.permissions import IsClient
from personal_training.serializers.client.session_cancellation import (
    SessionCancellationSerializer
)
from personal_training.services.client.session_cancellation_service import (
    SessionCancellationService
)


class SessionCancellationView(APIView):
    permission_classes = [IsClient]

    def post(self, request):
        serializer = SessionCancellationSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

            client = request.user
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

        except Exception:
            return Response(
                {"detail": "Something went wrong while canceling session."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
