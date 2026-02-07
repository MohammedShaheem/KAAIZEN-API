from rest_framework import serializers


class SessionTypeSelectionSerializer(serializers.Serializer):
    SESSION_CHOICES = ("morning", "evening")

    session_type = serializers.ChoiceField(choices=SESSION_CHOICES)

    def validate_session_type(self, value):
        if value not in self.SESSION_CHOICES:
            raise serializers.ValidationError("Invalid session type selected.")
        return value
