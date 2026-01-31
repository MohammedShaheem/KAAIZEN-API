from django.urls import path
from .views.nutrition import MealEntryCreateView,MealEntryListByDateView,DailyNutritionSummaryView
from .views.sleep import DailySleepCreateView,WeeklySleepReportView
urlpatterns = [
    path('meal-entries/', MealEntryCreateView.as_view()),
    path("meal-entries/<str:date>/",MealEntryListByDateView.as_view()),
    path("daily-summary/<str:date>/",DailyNutritionSummaryView.as_view()),
    path("sleep/",DailySleepCreateView.as_view()),
    path("sleep/weekly/", WeeklySleepReportView.as_view()),

]