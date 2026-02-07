from rest_framework import serializers


class SessionCancellationSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
