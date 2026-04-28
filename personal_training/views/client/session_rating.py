# personal_training/views.py (add to existing file)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from personal_training.models import TrainingSession
from personal_training.serializers.client.session_rating import SessionRatingSerializer


class RateSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        rating = request.data.get("rating")

        if not session_id or rating is None:
            return Response(
                {"detail": "session_id and rating are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        session = get_object_or_404(
            TrainingSession,
            id=session_id,
            client__user=request.user
        )

        serializer = SessionRatingSerializer(
            data={"rating": rating},
            context={"session": session}
        )
        serializer.is_valid(raise_exception=True)

        session.client_rating = serializer.validated_data["rating"]
        session.save(update_fields=["client_rating"])

        trainer = session.trainer
        avg = TrainingSession.objects.filter(
            trainer=trainer,
            client_rating__isnull=False
        ).aggregate(avg=Avg("client_rating"))["avg"]

        trainer.rating = round(avg, 2) if avg is not None else 0.00
        trainer.save(update_fields=["rating"])

        return Response(
            {"detail": "Rating submitted successfully.", "trainer_rating": trainer.rating},
            status=status.HTTP_200_OK
        )