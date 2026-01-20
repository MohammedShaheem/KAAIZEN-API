from django.urls import path
from workouts.views.sessions import StartWorkoutSessionView, CompleteWorkoutSessionView
from workouts.views.heartbeats import WorkoutHeartbeatView

urlpatterns = [
    path("sessions/start/", StartWorkoutSessionView.as_view()),
    path("sessions/heartbeat/", WorkoutHeartbeatView.as_view()),
    path("sessions/complete/", CompleteWorkoutSessionView.as_view()),
]
