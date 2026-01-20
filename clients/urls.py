from django.urls import path
from .views import ClientProfileView,MealAllocationsView
urlpatterns = [
    path("me/profile/",ClientProfileView.as_view()),
    path("meal-allocations/",MealAllocationsView.as_view(),name="meal-allocations"),
]
