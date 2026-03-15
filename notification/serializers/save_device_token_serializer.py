from rest_framework import serializers
from notification.models import UserDevice


class SaveDeviceTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Token is required.")

        if len(value) < 20:
            raise serializers.ValidationError("Invalid FCM token.")

        return value