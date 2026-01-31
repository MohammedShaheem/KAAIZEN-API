from django.urls import path
from ..views.client.sessions import StartWorkoutSessionView,CompleteWorkoutSessionView
from ..views.client.heartbeats import WorkoutHeartbeatView
from ..views.client.public_workouts import ClientWorkoutCategoryListView,ClientWorkoutListByCategoryView,ClientWorkoutDetailView

urlpatterns = [
    path("sessions/start/", StartWorkoutSessionView.as_view()),
    path("sessions/heartbeat/", WorkoutHeartbeatView.as_view()),
    path("sessions/complete/", CompleteWorkoutSessionView.as_view()),
    path("categories/", ClientWorkoutCategoryListView.as_view()),
    path("categories/<int:category_id>/workouts/", ClientWorkoutListByCategoryView.as_view()),
    path("workouts/<int:pk>/", ClientWorkoutDetailView.as_view()),
]
