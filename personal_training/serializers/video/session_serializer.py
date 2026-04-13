from rest_framework import serializers


class RecordingWebhookSerializer(serializers.Serializer):
    room_id = serializers.CharField()
    recording_url = serializers.URLField()