from django.urls import path
from trainers.views.profile import TrainerProfileView
from trainers.views.trainer_dashboard_view import TrainerDashboardView
from trainers.views.leaves_view import TrainerLeaveView

urlpatterns = [
    path('me/profile/',TrainerProfileView.as_view()),
    path("dashboard/",TrainerDashboardView.as_view()),
    path("leave/",TrainerLeaveView.as_view()),
    
]