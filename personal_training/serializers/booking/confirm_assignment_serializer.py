from rest_framework import serializers


class ConfirmAssignmentSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if value is not True:
            raise serializers.ValidationError("Confirmation required.")
        return value
