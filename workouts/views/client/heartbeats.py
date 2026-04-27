from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now
from workouts.serializers.sessions import HeartbeatSerializer
from kaaizen.settings import REDIS_CLIENT

class WorkoutHeartbeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HeartbeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        s = serializer.validated_data
        key = f"workout_session:{s['session_id']}"

        raw = REDIS_CLIENT.hgetall(key)
        if not raw:
            return Response({"detail": "Session expired"}, status=400)

        data = raw  
        if data["user_id"] != str(request.user.id):
            return Response(status=403)

        REDIS_CLIENT.hset(key, mapping={
            f"video:{s['workout_id']}:effective_seconds": s["effective_play_time_seconds"],
            f"video:{s['workout_id']}:last_position": s["current_video_time_seconds"],
            "last_heartbeat": now().isoformat(),
        })

        REDIS_CLIENT.expire(key, 7200)
        return Response({"status": "ok"})
