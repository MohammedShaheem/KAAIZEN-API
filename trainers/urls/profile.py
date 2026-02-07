from django.urls import path
from ..views.profile import TrainerProfileView
from trainers.views.trainer_dashboard_view import TrainerDashboardView

urlpatterns = [
    path('me/profile/',TrainerProfileView.as_view(), name='trainer-profile'),
    path("dashboard/",TrainerDashboardView.as_view()),
]