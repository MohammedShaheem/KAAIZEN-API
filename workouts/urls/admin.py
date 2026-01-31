from django.urls import path
from ..views.admin.admin_workouts import AdminWorkoutCategoryDetailView,AdminWorkoutCategoryListCreateView
from ..views.admin.admin_workouts import AdminWorkoutListCreateView,AdminWorkoutDetailView


urlpatterns = [
    path("categories/", AdminWorkoutCategoryListCreateView.as_view()),
    path("categories/<int:pk>/", AdminWorkoutCategoryDetailView.as_view()),
    path("workouts/", AdminWorkoutListCreateView.as_view()),
    path("workouts/<uuid:pk>/", AdminWorkoutDetailView.as_view()),
]
