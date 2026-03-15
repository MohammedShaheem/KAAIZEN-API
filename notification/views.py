from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from notification.serializers.save_device_token_serializer import SaveDeviceTokenSerializer
from notification.serializers.tracking_reminder_serializer import TrackingReminderSerializer
from notification.services.save_token_service import SaveTokenService

class CreateReminder(APIView):
    def post(self, request):
        serializer = TrackingReminderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)
    

class SaveDeviceTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SaveDeviceTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        SaveTokenService.save_device_token(
            user=request.user,
            token=token
        )

        return Response(
            {"message": "Device token saved successfully"},
            status=status.HTTP_200_OK,
        )