from django.urls import path
from admin_api.views import (
    AdminDashboardView,
    AdminClientListView,
    AdminClientDetailsView,
    AdminTrainerListView,
    AdminUserStatusView,
)


urlpatterns = [
    path("dashboard/",AdminDashboardView.as_view()),
    path("clients/",AdminClientListView.as_view()),
    path("clients/<uuid:user_id>/",AdminClientDetailsView.as_view()),
    path("trainers/",AdminTrainerListView.as_view()),
    path("users/<uuid:user_id>/status/", AdminUserStatusView.as_view()),
]
