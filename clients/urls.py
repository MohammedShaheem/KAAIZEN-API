from django.urls import path
from .views import ClientProfileView
urlpatterns = [
    path("me/profile/",ClientProfileView.as_view())

]
