from django.urls import path
from workouts.views.admin_workouts import (
    AdminWorkoutCategoryListCreateView,
    AdminWorkoutCategoryDetailView,
    AdminWorkoutListCreateView,
    AdminWorkoutDetailView,
)

urlpatterns = [
    path("categories/", AdminWorkoutCategoryListCreateView.as_view()),
    path("categories/<int:pk>/", AdminWorkoutCategoryDetailView.as_view()),
    path("workouts/", AdminWorkoutListCreateView.as_view()),
    path("workouts/<uuid:pk>/", AdminWorkoutDetailView.as_view()),
]
