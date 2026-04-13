import logging

from django.db import DatabaseError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ...models import TrainingSession
from ...services.video.session_service import VideoSessionService
from ...serializers.video.session_serializer import RecordingWebhookSerializer

logger = logging.getLogger(__name__)


class RecordingWebhookAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            serializer = RecordingWebhookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            room_id = serializer.validated_data["room_id"]
            recording_url = serializer.validated_data["recording_url"]

            session = TrainingSession.objects.filter(
                room_id=room_id
            ).first()

            if not session:
                return Response(
                    {"detail": "session not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            VideoSessionService.add_recording(session, recording_url)

            return Response({"ok": True}, status=status.HTTP_200_OK)

        except DatabaseError:
            logger.exception("Failed saving recording")
            return Response(
                {"detail": "failed to save recording"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )