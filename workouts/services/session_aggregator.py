from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now
from workouts.models import Workout

def aggregate_session(redis_client, session_key):
    raw = redis_client.hgetall(session_key)
    if not raw:
        raise ValueError("Session expired")
    
   
    data = raw
    videos = []
    for key, value in data.items():
        if key.startswith("video:") and key.endswith(":effective_seconds"):
            workout_id = key.split(":")[1]
            effective_seconds = int(value)

            workout = Workout.objects.get(id=workout_id)

            if effective_seconds < workout.duration_seconds * 0.3:
                continue  #ignoring little  watched videos

            videos.append({
                "workout": workout,
                "effective_seconds": effective_seconds,
                "met": workout.met_value,
            })

    return videos, data

