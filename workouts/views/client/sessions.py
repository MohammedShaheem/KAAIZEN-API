from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from uuid import uuid4
from django.utils.timezone import now
from workouts.serializers.sessions import StartSessionSerializer,CompleteSessionSerializer
from kaaizen.settings import REDIS_CLIENT
from workouts.services.calorie_calculator import calculate_calories
from workouts.models import WorkoutSession, SessionVideo
from workouts.services.session_aggregator import aggregate_session

class StartWorkoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = uuid4()
        key = f"workout_session:{session_id}"

        REDIS_CLIENT.hset(key, mapping={
            "user_id": str(request.user.id),
            "category_id": str(serializer.validated_data.get("category_id", "")),
            "started_at": now().isoformat(),
        })
        # expiry after 2 hours
        REDIS_CLIENT.expire(key, 7200)

        return Response({"session_id": session_id})
    
    
class CompleteWorkoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompleteSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]
        key = f"workout_session:{session_id}"

        videos, meta = aggregate_session(REDIS_CLIENT, key)

        start_time = now().fromisoformat(meta["started_at"]) 
        # how many time have been passed
        wall_clock = (now() - start_time).total_seconds()

        total_effective, calories = calculate_calories(
            videos,
            request.user.client_profile.weight_kg
        )

        if wall_clock < total_effective * 0.7:
            return Response({"detail": "Invalid completion"}, status=400)

        session = WorkoutSession.objects.create(
            id=session_id,
            user=request.user,
            status="completed",
            started_at=start_time,
            completed_at=now(),
            total_duration_seconds=total_effective,
            total_calories_burned=calories,
            notes=serializer.validated_data.get("notes", ""),
        )

        for v in videos:
            SessionVideo.objects.create(
                session=session,
                workout=v["workout"],
                effective_play_time_seconds=v["effective_seconds"],
            )

        REDIS_CLIENT.delete(key)
        return Response({"session_id": session.id, "calories": calories})