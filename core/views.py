import time
import cloudinary.utils
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings


# Create your views here.


# building signature for initially sendong to frontend
class CloudinarySignatureView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        upload_type = request.query_params.get("type", "raw")
        print("Entering here form cloudinary signature",upload_type)

        if upload_type not in ["raw", "video", "image"]:
            return Response(
                {"detail": "Invalid upload type"},
                status=400
            )

        timestamp = int(time.time())

        folder_map = {
            "raw": "trainer_certificates",
            "video": "workout _videos",
            "image": "profile_images",
        }

        params_to_sign = {
            "timestamp": timestamp,
            "folder": folder_map[upload_type],
            "access_mode": "public",
        }

        signature = cloudinary.utils.api_sign_request(
            params_to_sign,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )
        print("signature",signature)

        return Response({
            "signature": signature,
            "timestamp": timestamp,
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
            "api_key": settings.CLOUDINARY_API_KEY,
            "resource_type": upload_type,
            "folder": folder_map[upload_type],
        })
