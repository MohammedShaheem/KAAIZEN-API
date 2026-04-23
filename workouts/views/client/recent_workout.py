import logging
from django.db import DatabaseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from workouts.models import WorkoutSession
from workouts.serializers.recent_session import RecentSessionSerializer

logger = logging.getLogger(__name__)


class RecentWorkoutSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            sessions = (
                WorkoutSession.objects
                .filter(user=request.user)
                .select_related('category')
                .prefetch_related('session_videos')
                .order_by('-started_at')[:5]
            )
            
            print("session:",sessions)
            serializer = RecentSessionSerializer(sessions, many=True)

            return Response(
                {
                    "success": True,
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except DatabaseError as db_err:
            logger.error(f"Database error in RecentWorkoutSessionsView: {str(db_err)}")

            return Response(
                {
                    "success": False,
                    "message": "Database error occurred. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            logger.exception(f"Unexpected error in RecentWorkoutSessionsView: {str(e)}")

            return Response(
                {
                    "success": False,
                    "message": "Something went wrong. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )