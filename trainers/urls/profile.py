from django.urls import path
from ..views.profile import TrainerProfileView


urlpatterns = [
    path('me/profile/',TrainerProfileView.as_view(), name='trainer-profile'),
]