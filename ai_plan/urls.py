from django.urls import path
from ai_plan.views import GenerateAIPlanView

urlpatterns = [
    path("generate-ai-plan/", GenerateAIPlanView.as_view()),
]
