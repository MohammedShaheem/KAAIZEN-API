from django.urls import path
from .views import CreateReminder
from .views import SaveDeviceTokenView

urlpatterns = [
    path("create-reminder/", CreateReminder.as_view()),
    path("save-device-token/", SaveDeviceTokenView.as_view()),
    
]


