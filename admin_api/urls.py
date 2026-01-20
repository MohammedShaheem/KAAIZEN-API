from django.urls import path
from admin_api.views import (
    AdminDashboardView,
    AdminClientListView,
    AdminClientDetailsView,
    AdminTrainerListView,
    AdminUserStatusView,
    AdminTrainerDetailsView,
    AdminTrainerStatusView,
    PendingTrainerVerificationList,
    VerifyTrainerAPIView,
    TrainerVerificationDetailView
)


urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view()),

    path("clients/", AdminClientListView.as_view()),
    path("clients/<uuid:user_id>/", AdminClientDetailsView.as_view()),

    path("trainers/", AdminTrainerListView.as_view()),
    path("trainers/<uuid:user_id>/", AdminTrainerDetailsView.as_view()),

    path("users/<uuid:user_id>/status/", AdminUserStatusView.as_view()),
    path("trainers/<uuid:user_id>/status/", AdminTrainerStatusView.as_view()),
 
    path(
        "trainers/verification/",
        PendingTrainerVerificationList.as_view(),
    ),
    path(
        "trainers/verification/<uuid:pk>/",
        TrainerVerificationDetailView.as_view(),
    ),
    path(
        "trainers/verification/<uuid:pk>/action/",
        VerifyTrainerAPIView.as_view(),
    ),
]

