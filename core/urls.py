from django.urls import path
from .views import CloudinarySignatureView

urlpatterns = [
    path("cloudinary/",CloudinarySignatureView.as_view())
]
